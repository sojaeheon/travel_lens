# dags/currency_rate_update_dag.py
from datetime import datetime, timedelta, date

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from helpers.get_currency_naver import fetch_naver_fx_rates

POSTGRES_CONN_ID = "travel_postgres"


def update_currency_rates():
    """네이버 환율을 currency_history에 기록."""
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    conn = hook.get_conn()
    conn.autocommit = False

    # 1) DB에서 iso2 → currency_code 매핑 조회
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT iso2, currency_code, currency_unit_ko
            FROM currency
            """
        )
        target_data = cur.fetchall()

    print(f"[INFO] DB에서 {len(target_data)}개 행 조회")
    if target_data:
        print(f"[DEBUG] 샘플: {target_data[:3]}")

    # 2) 네이버 환율 조회
    fx_rates = fetch_naver_fx_rates()
    print(f"[DEBUG] 네이버 환율 개수: {len(fx_rates)}")
    if fx_rates:
        print(f"[DEBUG] 샘플 환율: {list(fx_rates.items())[:3]}")
    
    recorded_date = date.today().isoformat()

    # 3) 환율 매칭
    rows = []
    unmatched = []
    
    for iso2, currency_code, currency_unit_ko in target_data:
        if currency_code in fx_rates:
            krw_unit = fx_rates[currency_code]
            rows.append((iso2, currency_code, currency_unit_ko, krw_unit, recorded_date))
        else:
            unmatched.append((iso2, currency_code))

    print(f"[INFO] 매칭 완료: {len(rows)}개 성공, {len(unmatched)}개 실패")
    
    if unmatched:
        print(f"[DEBUG] 매칭 실패 목록: {unmatched[:5]}")

    if not rows:
        print("[INFO] No rows to insert.")
        conn.close()
        return

    # 4) INSERT
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO currency (iso2, currency_code, currency_unit_ko, currency_krw_unit, recorded_date)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (iso2, recorded_date) DO UPDATE
            SET currency_krw_unit = EXCLUDED.currency_krw_unit
            """,
            rows,
        )
    conn.commit()
    conn.close()
    print(f"[INFO] Inserted {len(rows)} currency history rows.")


default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="update_currency_rate_daily",
    default_args=default_args,
    schedule_interval="0 1 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["currency"],
) as dag:
    update_task = PythonOperator(
        task_id="update_currency_rates",
        python_callable=update_currency_rates,
    )