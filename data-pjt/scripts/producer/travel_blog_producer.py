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

# 11개 주요 여행 국가
TARGET_COUNTRIES = ['JP', 'VN', 'CN', 'TH', 'PH', 'US', 'TW', 'HK', 'SG', 'MY', 'AU']

# ✅ 확장된 검색 키워드
SEARCH_KEYWORDS = ["여행 추천", "맛집 리스트", "한달살기", "입국 후기", "가볼만한곳", "자유여행 코스", "여행 경비", "현지 날씨"]

# 수집 설정
LOOP_INTERVAL = 300
DISPLAY_LIMIT = 50  # 키워드당 수집 개수 상향
API_SLEEP = 0.2     # API 간격


def load_countries_from_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT,
        )
        with conn.cursor() as cur:
            cur.execute(
                "SELECT iso2, name_ko, continent_name_ko FROM country WHERE iso2 = ANY(%s) ORDER BY iso2",
                (TARGET_COUNTRIES,)
            )
            rows = cur.fetchall()
        conn.close()
        return [{"iso2": r[0], "name": r[1], "continent": r[2]} for r in rows]
    except Exception as e:
        print(f"[ERROR] DB Load Failed: {e}")
        return []


def create_producer_with_retry(retries: int = 10, delay: int = 3) -> KafkaProducer:
    for i in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
            )
            return producer
        except NoBrokersAvailable:
            time.sleep(delay)
    raise RuntimeError("Kafka broker not available")


def fetch_naver_blog(country: dict, keyword: str, limit: int):
    # ✅ 검색어 조합: "대륙 국가명 키워드"
    search_query = f"{country['continent']} {country['name']} {keyword}"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    
    # ✅ start 위치를 랜덤하게 주어 더 다양한 과거 데이터 수집
    params = {
        "query": search_query,
        "display": limit,
        "start": random.randint(1, 100),
        "sort": "date",
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
                "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),
                "url": item.get("link", ""),
                "postdate": item.get("postdate", ""),
                "fetched_at": datetime.utcnow().isoformat(),
            }
    except Exception as e:
        print(f"[ERROR] API error: {e}")


def main():
    try:
        producer = create_producer_with_retry()
    except RuntimeError as e:
        print(e); return

    countries = load_countries_from_db()
    loop_count = 0

    while True:
        try:
            loop_count += 1
            seen_urls = set()
            blog_count = 0
            print(f"\n[LOOP #{loop_count}] Blog Fetching Start...")

            for country in countries:
                for kw in SEARCH_KEYWORDS:
                    for blog in fetch_naver_blog(country, kw, DISPLAY_LIMIT):
                        url = blog.get("url")
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            producer.send(TOPIC, blog)
                            blog_count += 1
                    time.sleep(API_SLEEP)

            producer.flush()
            print(f"[LOOP #{loop_count}] Sent {blog_count} blogs. Wait {LOOP_INTERVAL}s")
            time.sleep(LOOP_INTERVAL)
        except Exception as e:
            print(f"[LOOP ERROR] {e}"); time.sleep(60)

if __name__ == "__main__":
    main()