import os
import time
import json
import random
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict

import requests
import psycopg2
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from dotenv import load_dotenv

print("🚀 [DEBUG] News Producer Script Initializing...")

load_dotenv()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
TOPIC = "travel_news"

TARGET_COUNTRIES = ['JP', 'VN', 'CN', 'TH', 'PH', 'US', 'TW', 'HK', 'SG', 'MY', 'AU']
NEWS_KEYWORDS = ["여행", "관광", "축제", "항공", "입국"]

LOOP_INTERVAL = 300 
REQUEST_SLEEP = 1

def load_countries_from_db():
    print("🔍 [DEBUG] Loading countries from DB...")
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        with conn.cursor() as cur:
            cur.execute("SELECT iso2, name_ko, continent_name_ko FROM country WHERE iso2 = ANY(%s)", (TARGET_COUNTRIES,))
            rows = cur.fetchall()
        conn.close()
        print(f"✅ [DEBUG] Loaded {len(rows)} countries.")
        return [{"iso2": r[0], "name": r[1], "continent": r[2]} for r in rows]
    except Exception as e:
        print(f"❌ [ERROR] DB Load Failed: {e}")
        return []

def create_producer_with_retry():
    print(f"🔍 [DEBUG] Connecting to Kafka at {KAFKA_BROKER}...")
    for i in range(5):
        try:
            p = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
                request_timeout_ms=5000
            )
            print("✅ [DEBUG] Kafka Connected.")
            return p
        except Exception as e:
            print(f"⚠️ [DEBUG] Kafka Connection Attempt {i+1} failed: {e}")
            time.sleep(2)
    return None

def fetch_google_news_rss(country: Dict, keyword: str):
    query = f"{country['continent']} {country['name']} {keyword}"
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
    try:
        resp = requests.get(rss_url, timeout=10)
        if resp.status_code != 200: return
        root = ET.fromstring(resp.content)
        items = root.findall(".//item")
        for item in items[:3]:
            yield {
                "iso2": country["iso2"],
                "country": country["name"],
                "title": item.find("title").text if item.find("title") is not None else "",
                "url": item.find("link").text if item.find("link") is not None else "",
                "published_at_raw": item.find("pubDate").text if item.find("pubDate") is not None else "",
                "fetched_at": datetime.utcnow().isoformat(),
            }
    except Exception as e:
        print(f"❌ [ERROR] RSS fetch error: {e}")

def main():
    print("🎬 [DEBUG] Main Loop Started.")
    producer = create_producer_with_retry()
    if not producer:
        print("❌ [FATAL] Kafka Producer creation failed.")
        return

    countries = load_countries_from_db()
    if not countries:
        print("❌ [FATAL] No countries found in DB.")
        return

    loop_count = 0
    while True:
        loop_count += 1
        news_count = 0
        print(f"\n[LOOP #{loop_count}] RSS News Fetching Start...")
        for country in countries:
            print(f"  -> Fetching: {country['name']}")
            for kw in NEWS_KEYWORDS:
                for news in fetch_google_news_rss(country, kw):
                    producer.send(TOPIC, news)
                    news_count += 1
                time.sleep(REQUEST_SLEEP)
        producer.flush()
        print(f"✅ [LOOP #{loop_count}] Sent {news_count} news items.")
        time.sleep(LOOP_INTERVAL)

if __name__ == "__main__":
    print("🏁 [DEBUG] Entry point reached.")
    main()