# scripts/consumer/travel_blog_consumer.py

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

# .env 에서 읽기
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC = "travel_blogs"

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")


def parse_postdate(s: str):
    """네이버 postdate = 'YYYYMMDD' 형식을 timestamptz 로 바꾸기."""
    try:
        return datetime.strptime(s, "%Y%m%d")
    except Exception:
        return None


def create_consumer_with_retry(retries: int = 10, delay: int = 3) -> KafkaConsumer:
    """카프카 브로커 준비될 때까지 재시도하면서 KafkaConsumer 생성."""
    for i in range(retries):
        try:
            print(f"[INFO] Try connecting KafkaConsumer ({i+1}/{retries}) to {KAFKA_BROKER}")
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=KAFKA_BROKER,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",  # 처음부터 읽고 싶으면 earliest
                enable_auto_commit=True,
                group_id="blog-consumer",
            )
            print("[INFO] KafkaConsumer connected")
            return consumer
        except NoBrokersAvailable:
            print("[WARN] NoBrokersAvailable (consumer), retrying in", delay, "seconds...")
            time.sleep(delay)
    raise RuntimeError("Kafka broker not available for consumer after retries")


def main():
    # Kafka Consumer 설정 (재시도 포함)
    consumer = create_consumer_with_retry()

    # Postgres 연결
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    conn.autocommit = False

    buffer = []
    BATCH_SIZE = 100

    print("[INFO] Blog consumer started")

    try:
        for msg in consumer:
            blog = msg.value

            iso2 = blog.get("iso2")
            title = blog.get("title")
            url = blog.get("url")
            postdate_str = blog.get("postdate", "")

            # 필수 필드 없으면 스킵
            if not url or not title or not iso2:
                continue

            published_at = parse_postdate(postdate_str)

            buffer.append((iso2, title, url, published_at))

            if len(buffer) >= BATCH_SIZE:
                with conn.cursor() as cur:
                    execute_batch(
                        cur,
                        """
                        INSERT INTO destination_blog (iso2, title, url, published_at)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (url) DO NOTHING
                        """,
                        buffer,
                    )
                conn.commit()
                print(f"[INFO] Inserted batch of {len(buffer)} blogs")
                buffer.clear()

    except KeyboardInterrupt:
        print("[INFO] Stopping consumer (KeyboardInterrupt)")
    finally:
        # 남아 있는 데이터 flush
        if buffer:
            with conn.cursor() as cur:
                execute_batch(
                    cur,
                    """
                    INSERT INTO destination_blog (iso2, title, url, published_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING
                    """,
                    buffer,
                )
            conn.commit()
            print(f"[INFO] Inserted remaining {len(buffer)} blogs")

        conn.close()


if __name__ == "__main__":
    main()
