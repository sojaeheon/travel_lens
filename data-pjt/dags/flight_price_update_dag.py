# dags/flight_price_update_dag.py
from datetime import datetime, date, timedelta
import time

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from helpers.get_flight_price import get_lowest_price


POSTGRES_CONN_ID = "travel_postgres"

def update_flight_prices():
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

    # ✅ 수정: currency 테이블과 조인
    airports = hook.get_records(
        """
        SELECT a.id, a.airport_code_iata
        FROM airport a
        INNER JOIN country c ON a.iso2 = c.iso2
        INNER JOIN currency curr ON c.iso2 = curr.iso2
        WHERE a.airport_code_iata IS NOT NULL
        AND (
            curr.currency_code = 'EUR'
            OR curr.currency_krw_unit IS NOT NULL  -- 네이버 환율 업데이트된 통화
        )
        """
    )

    target_date = date.today().isoformat()
    updated_count = 0

    for airport_id, airport_code in airports:
        price = get_lowest_price(airport_code, origin_airport_code="ICN", target_date=target_date)

        if price is None:
            continue

        hook.run(
            "UPDATE airport SET flight_price = %s WHERE id = %s",
            parameters=(price, airport_id),
        )

        time.sleep(0.12)

    print(f"[INFO] Updated {updated_count} flight prices")


default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="update_flight_price_daily",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 3 * * *",
    catchup=False,
) as dag:
    update_prices = PythonOperator(
        task_id="update_flight_prices",
        python_callable=update_flight_prices,
    )