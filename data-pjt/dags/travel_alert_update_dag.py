# dags/travel_alert_update_dag.py
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from helpers.get_travel_alert import fetch_travel_alarm
from helpers.parse_travel_alarm import parse_travel_alerts

POSTGRES_CONN_ID = "travel_postgres"


def update_travel_alerts():
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    conn = hook.get_conn()
    conn.autocommit = False

    # 1) country 테이블에서 iso2 목록 가져오기
    with conn.cursor() as cur:
        cur.execute("SELECT iso2 FROM country WHERE iso2 IS NOT NULL")
        iso2_list = [row[0] for row in cur.fetchall()]

    buffer = []

    # 2) iso2 별로 외교부 API 호출 → 파싱
    for iso2 in iso2_list:
        raw = fetch_travel_alarm(iso2=iso2, page=1, per_page=100)
        # totalCount=0 이면 parse_travel_alerts 가 빈 리스트 반환
        rows = parse_travel_alerts(raw, iso2=iso2)
        buffer.extend(rows)

    if not buffer:
        print("[INFO] No travel alerts parsed.")
        return

    # 3) travel_alert 테이블에 UPSERT
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO travel_alert (iso2, alarm_level, region, updated_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (iso2) DO UPDATE
                SET alarm_level = EXCLUDED.alarm_level,
                    region      = EXCLUDED.region,
                    updated_at  = EXCLUDED.updated_at
            """,
            buffer,
        )
    conn.commit()
    conn.close()
    print(f"[INFO] Upserted {len(buffer)} travel_alert rows.")


# ✅ DAG 정의
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="update_travel_alert_daily",
    default_args=default_args,
    schedule_interval="0 2 * * *",  # 매일 02:00
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["alert"],
) as dag:
    update_alerts = PythonOperator(
        task_id="update_travel_alerts",
        python_callable=update_travel_alerts,
    )
