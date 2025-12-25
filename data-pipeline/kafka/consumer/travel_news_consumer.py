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
from email.utils import parsedate_to_datetime # RSS 날짜 파싱용 추가

load_dotenv()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC = "travel_news"

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

# ✅ TARGET_COUNTRIES: 11개 주요 여행 국가만
TARGET_COUNTRIES = ['JP', 'VN', 'CN', 'TH', 'PH', 'US', 'TW', 'HK', 'SG', 'MY', 'AU']


def parse_published_at(s: str):
    if not s:
        return None
    try:
        # 1. ISO 형식 시도 (기존 방식)
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except:
        try:
            # 2. RSS (RFC 2822) 형식 시도 (새로운 방식)
            return parsedate_to_datetime(s)
        except Exception as e:
            print(f"[WARN] Failed to parse date '{s}': {e}")
            return None


def parse_fetched_at(s: str | None):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception as e:
        print(f"[WARN] Failed to parse fetched_at '{s}': {e}")
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
                session_timeout_ms=30000,  # ✅ 세션 타임아웃 추가
            )
            print("[INFO] News KafkaConsumer connected successfully")
            return consumer
        except NoBrokersAvailable:
            print(f"[WARN] NoBrokersAvailable (news consumer), retrying in {delay} seconds...")
            time.sleep(delay)
    
    raise RuntimeError("Kafka broker not available for news consumer after retries")


def main():
    # Kafka Consumer 설정 (재시도 포함)
    try:
        consumer = create_consumer_with_retry()
    except RuntimeError as e:
        print(f"[FATAL] {e}")
        return

    # PostgreSQL 연결
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn.autocommit = False
    except Exception as e:
        print(f"[FATAL] Failed to connect to PostgreSQL: {e}")
        return

    buffer = []
    BATCH_SIZE = 10
    stats = {"total": 0, "inserted": 0, "skipped": 0, "failed": 0}

    print("[INFO] News consumer started")
    print(f"[INFO] Target countries: {TARGET_COUNTRIES}")
    print(f"[INFO] Batch size: {BATCH_SIZE}")
    print("="*60)

    try:
        for msg in consumer:
            news = msg.value

            iso2 = news.get("iso2")
            title = news.get("title")
            url = news.get("url")
            published_at_raw = news.get("published_at_raw", "")
            fetched_at = news.get("fetched_at")

            stats["total"] += 1

            # ✅ 필수 필드 검증
            if not iso2 or not title or not url:
                print(f"[SKIP] Missing required fields: iso2={iso2}, title={bool(title)}, url={bool(url)}")
                stats["skipped"] += 1
                continue

            # ✅ TARGET_COUNTRIES 필터링
            if iso2 not in TARGET_COUNTRIES:
                print(f"[SKIP] Not in TARGET_COUNTRIES: {iso2}")
                stats["skipped"] += 1
                continue

            # ✅ published_at을 datetime으로 변환 (psycopg2가 자동으로 timestamptz 변환)
            published_at = parse_published_at(published_at_raw) or parse_fetched_at(fetched_at)

            buffer.append((iso2, title, url, published_at))

            # ✅ Batch INSERT (10개씩 모아서 한 번에)
            if len(buffer) >= BATCH_SIZE:
                try:
                    with conn.cursor() as cur:
                        execute_batch(
                            cur,
                            """
                            INSERT INTO destination_news (iso2, title, url, published_at)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (url) DO UPDATE
                            SET published_at = EXCLUDED.published_at
                            """,
                            buffer,
                        )
                    conn.commit()
                    stats["inserted"] += len(buffer)
                    print(
                        f"[BATCH] Inserted {len(buffer)} news | "
                        f"Total: {stats['total']}, Inserted: {stats['inserted']}, "
                        f"Skipped: {stats['skipped']}, Failed: {stats['failed']}"
                    )
                    buffer.clear()

                except Exception as e:
                    conn.rollback()
                    stats["failed"] += len(buffer)
                    print(f"[ERROR] Batch insert failed: {e}")
                    buffer.clear()

    except KeyboardInterrupt:
        print("\n[INFO] Stopping news consumer (KeyboardInterrupt)")

    except Exception as e:
        print(f"[ERROR] Consumer error: {e}")

    finally:
        # ✅ 남아 있는 데이터 flush
        if buffer:
            try:
                with conn.cursor() as cur:
                    execute_batch(
                        cur,
                        """
                        INSERT INTO destination_news (iso2, title, url, published_at)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (url) DO UPDATE
                        SET published_at = EXCLUDED.published_at
                        """,
                        buffer,
                    )
                conn.commit()
                stats["inserted"] += len(buffer)
                print(f"[FLUSH] Inserted remaining {len(buffer)} news")

            except Exception as e:
                stats["failed"] += len(buffer)
                print(f"[ERROR] Final flush failed: {e}")

        conn.close()
        consumer.close()

        print("\n" + "="*60)
        print(
            f"[SUMMARY] Total received: {stats['total']}, "
            f"Inserted: {stats['inserted']}, "
            f"Skipped: {stats['skipped']}, "
            f"Failed: {stats['failed']}"
        )


if __name__ == "__main__":
    main()
