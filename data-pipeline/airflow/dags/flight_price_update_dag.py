# dags/flight_price_update_dag.py
from datetime import datetime, date, timedelta
import time

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from helpers.get_flight_price import get_lowest_price


POSTGRES_CONN_ID = "travel_postgres"

# 11개 주요 여행 국가 (get_flight_price.py와 동일하게 유지)
TARGET_COUNTRIES = ['JP', 'VN', 'CN', 'TH', 'PH', 'US', 'TW', 'HK', 'SG', 'MY', 'AU']


def update_flight_prices():
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    conn = hook.get_conn()
    conn.autocommit = False

    # 1) 11개 주요 국가에 해당하는 공항 정보만 조회
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT iso2, airport_code_iata, airport_name_ko
            FROM target_country
            WHERE iso2 = ANY(%s)
              AND airport_code_iata IS NOT NULL
            ORDER BY iso2
            """,
            (TARGET_COUNTRIES,)
        )
        airports = cur.fetchall()
    
    print(f"[INFO] DB에서 {len(airports)}개 공항 조회 (11개 주요 국가)")

    target_date = date.today().isoformat()
    insert_rows = []

    for iso2, airport_code, airport_name_ko in airports:
        price = get_lowest_price(airport_code, origin_airport_code="ICN", target_date=target_date)

        if price is None:
            print(f"[SKIP] {iso2} ({airport_code}): 가격 없음")
            continue

        insert_rows.append((iso2, airport_name_ko, airport_code, price, target_date))
        print(f"[OK] {iso2} ({airport_code}): {price:,.0f} KRW")

        time.sleep(0.5)  # API Rate Limiting (0.12 → 0.5초로 증가)

    if not insert_rows:
        print("[INFO] No prices to insert.")
        conn.close()
        return

    # 2) flight_history에 INSERT
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO airport (
                iso2,
                airport_name_ko,
                airport_code_iata,
                flight_price,
                recorded_date
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (iso2, airport_code_iata, recorded_date)
            DO UPDATE SET
                flight_price = EXCLUDED.flight_price
            """,
            insert_rows,
        )
    conn.commit()
    conn.close()
    print(f"[INFO] Inserted {len(insert_rows)} flight price history rows.")


default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="update_flight_price_daily",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 3 * * *",  # 매일 새벽 3시
    catchup=False,
    tags=["travel", "flight-price"],
) as dag:
    update_prices = PythonOperator(
        task_id="update_flight_prices",
        python_callable=update_flight_prices,
    )