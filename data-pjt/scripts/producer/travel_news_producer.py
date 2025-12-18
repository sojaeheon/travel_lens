# scripts/producer/travel_news_producer.py

import os
import time
import json
import random
from datetime import datetime
from typing import List, Dict

import requests
import psycopg2
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urljoin

load_dotenv()

# 환경 변수
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

TOPIC = "travel_news"

NEWS_BASE_URL = "https://news.google.com/"

# 수집 속도 / 주기 설정 (구글 차단 방지용, 느리게!)
LOOP_INTERVAL = 600            # 10분마다 전체 루프
COUNTRY_BATCH_SIZE = 10        # 루프당 10개 나라만
NEWS_PER_COUNTRY = 3           # 나라당 3개 뉴스
REQUEST_SLEEP_MIN = 5          # 요청 사이 최소 5초
REQUEST_SLEEP_MAX = 10         # 요청 사이 최대 10초


def load_countries_from_db() -> List[Dict]:
    """country 테이블에서 iso2 / 나라명 / 대륙명 읽어오기."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT iso2, name_ko, continent_name_ko
            FROM country
            """
        )
        rows = cur.fetchall()
    conn.close()

    countries = []
    for iso2, name, continent in rows:
        countries.append(
            {
                "iso2": iso2,
                "name": name,
                "continent": continent,
            }
        )
    print(f"[INFO] Loaded {len(countries)} countries from DB (for news)")
    return countries


def create_producer_with_retry(retries: int = 10, delay: int = 3) -> KafkaProducer:
    """카프카 브로커 준비될 때까지 재시도하면서 KafkaProducer 생성."""
    for i in range(retries):
        try:
            print(f"[INFO] Try connecting KafkaProducer ({i + 1}/{retries}) to {KAFKA_BROKER}")
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
            )
            print("[INFO] KafkaProducer connected (news)")
            return producer
        except NoBrokersAvailable:
            print("[WARN] NoBrokersAvailable (news producer), retrying in", delay, "seconds...")
            time.sleep(delay)
    raise RuntimeError("Kafka broker not available for news producer after retries")


def parse_google_news_html(html: str, limit: int) -> list[dict]:
    """
    Google News 검색 결과 HTML에서 뉴스 제목/URL/발행시간 일부를 파싱.
    """
    soup = BeautifulSoup(html, "html.parser")
    results: list[dict] = []

    # 기사 카드 선택자 (Google News 마크업에 따라 필요시 조정)
    cards = soup.select("article, div.xrnccd, div.IFHyqb")

    for card in cards:
        # 제목 링크
        a = card.select_one("a[role=heading], a.DY5T1d, a.JtKRv")
        if not a:
            a = card.find("a")
        if not a:
            continue

        title = a.get_text(strip=True)
        href = a.get("href")
        if not href:
            continue

        url = urljoin(NEWS_BASE_URL, href)

        # 발행 시간 태그
        time_tag = card.find("time")
        # datetime 속성이 있으면 그 값을 사용 (ISO8601 형태일 가능성이 높음)
        published_at_raw = time_tag.get("datetime") if time_tag else None

        results.append(
            {
                "title": title,
                "url": url,
                "published_at_raw": published_at_raw,
            }
        )

        if len(results) >= limit:
            break

    return results


def fetch_google_news(country: Dict, limit: int = NEWS_PER_COUNTRY):
    """
    구글 뉴스 검색 결과 일부를 긁어서 뉴스 목록으로 yield.
    실제 프로덕션에서는 공식 API/타사 뉴스 API 사용을 고려해야 하고,
    구글 서비스 약관 및 robots.txt를 반드시 확인해야 한다.
    """
    # 예시 검색어: "유럽 프랑스 여행 뉴스"
    query = f"{country['continent']} {country['name']} 여행 뉴스"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) "
            "Gecko/20100101 Firefox/124.0"
        )
    }

    params = {
        "q": query,
        "hl": "ko",
        "gl": "KR",
        "ceid": "KR:ko",
    }

    url = "https://news.google.com/search"

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()

        html = resp.text
        # 디버깅용으로 HTML 저장 (필요 없으면 주석 처리 가능)
        with open("news_sample.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("[DEBUG] Saved news_sample.html")

        # 실제 파싱
        parsed_news = parse_google_news_html(html, limit=limit)

        for item in parsed_news:
            yield {
                "iso2": country["iso2"],
                "country": country["name"],
                "continent": country["continent"],
                "search_keyword": query,
                "title": item["title"],
                "url": item["url"],
                # published_at_raw: HTML에서 추출한 값 (없으면 None)
                "published_at_raw": item.get("published_at_raw"),
                # 프로듀서 fetch 시간 (UTC)
                "fetched_at": datetime.utcnow().isoformat(),
            }

    except Exception as e:
        print(f"[ERROR] Google News fetch error for {query}: {e}")


def main():
    producer = create_producer_with_retry()
    countries = load_countries_from_db()
    if not countries:
        print("[ERROR] No countries loaded from DB for news; exiting")
        return

    seen_urls = set()

    while True:
        try:
            batch_size = min(COUNTRY_BATCH_SIZE, len(countries))
            batch = random.sample(countries, k=batch_size)

            print(f"[INFO] News loop - fetching news for {batch_size} countries")

            for country in batch:
                for news in fetch_google_news(country):
                    url = news.get("url")
                    if not url:
                        continue
                    if url in seen_urls:
                        continue

                    seen_urls.add(url)
                    producer.send(TOPIC, news)
                    print(
                        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
                        f"Sent news ({country['continent']} {country['name']}) {news['title']}"
                    )

                sleep_sec = random.uniform(REQUEST_SLEEP_MIN, REQUEST_SLEEP_MAX)
                print(f"[INFO] Sleep {sleep_sec:.1f}s between countries for Google News")
                time.sleep(sleep_sec)

            producer.flush()
            print(f"[INFO] News loop finished. Sleep {LOOP_INTERVAL} seconds.")
            time.sleep(LOOP_INTERVAL)

        except Exception as e:
            print("[NEWS LOOP ERROR]", e)
            time.sleep(60)


if __name__ == "__main__":
    main()
