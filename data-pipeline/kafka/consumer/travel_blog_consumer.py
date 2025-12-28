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
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

# 11개 타겟 국가 (필터링용)
TARGET_COUNTRIES = ['JP', 'VN', 'CN', 'TH', 'PH', 'US', 'TW', 'HK', 'SG', 'MY', 'AU']


def parse_postdate(s: str):
    """
    네이버 postdate = 'YYYYMMDD' 형식을 datetime으로 변환.
    PostgreSQL이 자동으로 timestamptz로 변환함.
    실패하면 None 반환.
    """
    if not s:
        return None
    try:
        # ✅ datetime 객체 반환 (psycopg2가 자동으로 timestamptz 변환)
        return datetime.strptime(s, "%Y%m%d")
    except Exception as e:
        print(f"[WARN] Failed to parse postdate '{s}': {e}")
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
            print(f"[INFO] Try connecting KafkaConsumer ({i+1}/{retries}) to {KAFKA_BROKER}")
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=KAFKA_BROKER,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest", 
                enable_auto_commit=True,
                group_id="blog-consumer",
                session_timeout_ms=30000,
            )
            print("[INFO] KafkaConsumer connected successfully")
            return consumer
        except NoBrokersAvailable:
            print(f"[WARN] NoBrokersAvailable (consumer), retrying in {delay} seconds...")
            time.sleep(delay)
    
    raise RuntimeError("Kafka broker not available for consumer after retries")


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

    print("[INFO] Blog consumer started")
    print(f"[INFO] Target countries: {TARGET_COUNTRIES}")
    print(f"[INFO] Batch size: {BATCH_SIZE}")
    print("="*60)

    try:
        for msg in consumer:
            blog = msg.value

            iso2 = blog.get("iso2")
            title = blog.get("title")
            url = blog.get("url")
            postdate_str = blog.get("postdate", "")
            fetched_at = blog.get("fetched_at")

            stats["total"] += 1

            # ✅ 필수 필드 검증
            if not url or not title or not iso2:
                print(f"[SKIP] Missing required fields: iso2={iso2}, title={bool(title)}, url={bool(url)}")
                stats["skipped"] += 1
                continue

            # ✅ TARGET_COUNTRIES 필터링
            if iso2 not in TARGET_COUNTRIES:
                print(f"[SKIP] Not in TARGET_COUNTRIES: {iso2}")
                stats["skipped"] += 1
                continue

            # ✅ published_at을 datetime으로 변환 (psycopg2가 자동으로 timestamptz 변환)
            published_at = parse_fetched_at(fetched_at) or parse_postdate(postdate_str)

            buffer.append((iso2, title, url, published_at))

            # ✅ Batch INSERT (100개씩 모아서 한 번에)
            if len(buffer) >= BATCH_SIZE:
                try:
                    with conn.cursor() as cur:
                        execute_batch(
                            cur,
                            """
                            INSERT INTO destination_blog (iso2, title, url, published_at)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (url) DO UPDATE
                            SET published_at = EXCLUDED.published_at
                            """,
                            buffer,
                        )
                    conn.commit()
                    stats["inserted"] += len(buffer)
                    print(
                        f"[BATCH] Inserted {len(buffer)} blogs | "
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
        print("\n[INFO] Stopping consumer (KeyboardInterrupt)")
    
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
                        INSERT INTO destination_blog (iso2, title, url, published_at)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (url) DO UPDATE
                        SET published_at = EXCLUDED.published_at
                        """,
                        buffer,
                    )
                conn.commit()
                stats["inserted"] += len(buffer)
                print(f"[FLUSH] Inserted remaining {len(buffer)} blogs")
            
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
