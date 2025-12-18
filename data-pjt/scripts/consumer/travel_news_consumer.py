# scripts/consumer/travel_news_consumer.py

import json
import os
import time
from datetime import datetime

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv

load_dotenv()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC = "travel_news"

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")


def parse_published_at(s: str):
    """published_at_raw 문자열을 datetime 으로 변환 (필요에 맞게 조정)."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception as e:
        print(f"[WARN] Failed to parse published_at_raw='{s}': {e}")
        return None



def create_consumer_with_retry(retries: int = 10, delay: int = 3) -> KafkaConsumer:
    """카프카 브로커 준비될 때까지 재시도하면서 KafkaConsumer 생성."""
    for i in range(retries):
        try:
            print(f"[INFO] Try connecting News KafkaConsumer ({i+1}/{retries}) to {KAFKA_BROKER}")
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=KAFKA_BROKER,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                group_id="news-consumer",
            )
            print("[INFO] News KafkaConsumer connected")
            return consumer
        except NoBrokersAvailable:
            print("[WARN] NoBrokersAvailable (news consumer), retrying in", delay, "seconds...")
            time.sleep(delay)
    raise RuntimeError("Kafka broker not available for news consumer after retries")


def main():
    consumer = create_consumer_with_retry()

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    conn.autocommit = False

    buffer = []
    BATCH_SIZE = 10

    print("[INFO] News consumer started")

    try:
        for msg in consumer:
            news = msg.value

            iso2 = news.get("iso2")
            title = news.get("title")
            url = news.get("url")
            published_at_raw = news.get("published_at_raw", "")

            if not iso2 or not title or not url:
                continue

            published_at = parse_published_at(published_at_raw)

            buffer.append((iso2, title, url, published_at))

            if len(buffer) >= BATCH_SIZE:
                with conn.cursor() as cur:
                    execute_batch(
                        cur,
                        """
                        INSERT INTO destination_news (iso2, title, url, published_at)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (url) DO NOTHING
                        """,
                        buffer,
                    )
                conn.commit()
                print(f"[INFO] Inserted news batch of {len(buffer)} rows")
                buffer.clear()

    except KeyboardInterrupt:
        print("[INFO] Stopping news consumer (KeyboardInterrupt)")
    finally:
        if buffer:
            with conn.cursor() as cur:
                execute_batch(
                    cur,
                    """
                    INSERT INTO destination_news (iso2, title, url, published_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING
                    """,
                    buffer,
                )
            conn.commit()
            print(f"[INFO] Inserted remaining {len(buffer)} news rows")

        conn.close()


if __name__ == "__main__":
    main()
