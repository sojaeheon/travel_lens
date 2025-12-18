# dags/currency_rate_update_dag.py
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from helpers.get_currency_naver import build_update_rows

POSTGRES_CONN_ID = "travel_postgres"


def update_currency_rates():
    """네이버 환율 데이터를 읽어서 currency 테이블 갱신."""
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    conn = hook.get_conn()
    conn.autocommit = False

    rows = build_update_rows()  # [(currency_krw_unit, updated_at, currency_code), ...]
    if not rows:
        print("[INFO] No FX rows to update.")
        return

    with conn.cursor() as cur:
        # currency_code 기준으로 환율/갱신일시 업데이트
        cur.executemany(
            """
            UPDATE currency
            SET currency_krw_unit = %s,
                updated_at = %s
            WHERE currency_code = %s
            """,
            rows,
        )
    conn.commit()
    conn.close()
    print(f"[INFO] Updated {len(rows)} currency rows.")


default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="update_currency_rate_daily",
    default_args=default_args,
    schedule_interval="0 1 * * *",  # 매일 01:00
    start_date=datetime(2024, 12, 1),
    catchup=False,
    tags=["currency"],
) as dag:
    update_task = PythonOperator(
        task_id="update_currency_rates",
        python_callable=update_currency_rates,
    )
