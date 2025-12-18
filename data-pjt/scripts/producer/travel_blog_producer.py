# scripts/producer/travel_blog_kafka_producer.py

import time
import json
import random
import os
from datetime import datetime

import requests
import psycopg2
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from dotenv import load_dotenv

load_dotenv()

# 환경 변수
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

TOPIC = "travel_blogs"

# 수집 주기/속도 설정
LOOP_INTERVAL = 300          # 5분마다 루프
COUNTRY_BATCH_SIZE = 60      # 루프당 60개 나라
DISPLAY_LIMIT = 5            # 나라당 5개 문서
API_SLEEP = 0.1              # 나라 호출 사이 0.1초 대기


def load_countries_from_db():
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
    print(f"[INFO] Loaded {len(countries)} countries from DB")
    return countries


def create_producer_with_retry(retries: int = 10, delay: int = 3) -> KafkaProducer:
    """카프카 브로커 준비될 때까지 재시도하면서 KafkaProducer 생성."""
    for i in range(retries):
        try:
            print(f"[INFO] Try connecting KafkaProducer ({i+1}/{retries}) to {KAFKA_BROKER}")
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
            )
            print("[INFO] KafkaProducer connected")
            return producer
        except NoBrokersAvailable:
            print("[WARN] NoBrokersAvailable, retrying in", delay, "seconds...")
            time.sleep(delay)
    raise RuntimeError("Kafka broker not available after retries")


# ✅ 여기서 바로 KafkaProducer 만들지 말고, main() 안에서 위 함수로 생성
producer = None  # 전역 변수 자리만 잡아두기


def fetch_naver_blog(country: dict, limit: int = DISPLAY_LIMIT):
    """네이버 블로그 검색 API 호출."""
    search_query = f"{country['continent']} {country['name']} 여행"

    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }

    params = {
        "query": search_query,
        "display": limit,
        "start": 1,
        "sort": "date",  # 최신순
    }

    url = "https://openapi.naver.com/v1/search/blog"

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("items", []):
            yield {
                "iso2": country["iso2"],
                "country": country["name"],
                "continent": country["continent"],
                "search_keyword": search_query,
                "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),
                "url": item.get("link", ""),
                "description": item.get("description", "").replace("<b>", "").replace("</b>", ""),
                "bloggername": item.get("bloggername", ""),
                "bloggerlink": item.get("bloggerlink", ""),
                "postdate": item.get("postdate", ""),  # "YYYYMMDD" 문자열
                "fetched_at": datetime.utcnow().isoformat(),
            }
    except Exception as e:
        print(f"[ERROR] API error for {search_query}: {e}")


def main():
    global producer

    # 1) 카프카 프로듀서 연결 (재시도 포함)
    producer = create_producer_with_retry()

    # 2) 국가 목록 로드
    countries = load_countries_from_db()
    if not countries:
        print("[ERROR] No countries loaded from DB; exiting")
        return

    seen_urls = set()

    while True:
        try:
            batch_size = min(COUNTRY_BATCH_SIZE, len(countries))
            batch = random.sample(countries, k=batch_size)

            print(f"[INFO] New loop - fetching blogs for {batch_size} countries")

            for country in batch:
                for blog in fetch_naver_blog(country):
                    url = blog.get("url")
                    if not url:
                        continue

                    if url in seen_urls:
                        continue

                    seen_urls.add(url)
                    producer.send(TOPIC, blog)
                    print(
                        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
                        f"Sent ({country['continent']} {country['name']}) {blog['title']}"
                    )

                time.sleep(API_SLEEP)

            producer.flush()
            time.sleep(LOOP_INTERVAL)

        except Exception as e:
            print("[LOOP ERROR]", e)
            time.sleep(60)


if __name__ == "__main__":
    main()
