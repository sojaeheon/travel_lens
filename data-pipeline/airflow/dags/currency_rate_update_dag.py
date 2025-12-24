# dags/currency_rate_update_dag.py
from datetime import datetime, timedelta, date

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from helpers.get_currency_naver import fetch_naver_fx_rates

POSTGRES_CONN_ID = "travel_postgres"


def update_currency_rates():
    """
    네이버 환율을 크롤링하여 currency_history를 UPDATE.
    각 국가당 1개 행만 유지, recorded_date는 최신화 시각 기록.
    """
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    conn = hook.get_conn()
    conn.autocommit = False

    # 1) target_country에서 iso2, currency_code 조회
    with conn.cursor() as cur:
        cur.execute("""
            SELECT iso2, currency_code
            FROM target_country
            ORDER BY iso2
        """)
        target_countries = cur.fetchall()

    print(f"[INFO] target_country에서 {len(target_countries)}개 국가 조회")

    # 2) 네이버 환율 조회
    fx_rates = fetch_naver_fx_rates()
    print(f"[INFO] 네이버 환율 {len(fx_rates)}개 조회")
    
    if not fx_rates:
        print("[ERROR] 네이버 환율 조회 실패!")
        conn.close()
        return
    
    today = date.today()

    # 3) 환율 매칭 및 UPDATE 데이터 준비
    update_rows = []
    matched_count = 0
    unmatched = []
    
    for iso2, currency_code in target_countries:
        if currency_code in fx_rates:
            krw_unit = fx_rates[currency_code]
            update_rows.append((
                iso2,           # iso2 (FK)
                currency_code,  # 통화 코드
                krw_unit,       # 환율
                today           # 날짜
            ))
            matched_count += 1
            print(f"[MATCH] {iso2} ({currency_code}): {krw_unit} KRW")
        else:
            unmatched.append((iso2, currency_code))
            print(f"[MISS] {iso2} ({currency_code}): 환율 정보 없음")

    print(f"\n[SUMMARY] 매칭 성공: {matched_count}개, 실패: {len(unmatched)}개")
    
    if unmatched:
        print(f"[WARNING] 매칭 실패 목록: {unmatched}")

    if not update_rows:
        print("[INFO] 업데이트할 환율 데이터가 없습니다.")
        conn.close()
        return

    # 4) currency_history에 INSERT or UPDATE (국가당 1개 행 유지)
    # 4) currency 테이블에 INSERT or UPDATE
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO currency (
                iso2,
                currency_code,
                currency_krw_unit,
                recorded_date
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (iso2, recorded_date)
            DO UPDATE SET
                currency_krw_unit = EXCLUDED.currency_krw_unit;
        """, update_rows)

    
    conn.commit()
    conn.close()
    
    print(f"[SUCCESS] {len(update_rows)}개 환율 데이터를 업데이트했습니다 (최신화 일자: {today}).")


default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="update_currency_rate_daily",
    default_args=default_args,
    schedule_interval="0 1 * * *",  # 매일 새벽 1시
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["currency", "travel"],
) as dag:
    
    update_task = PythonOperator(
        task_id="update_currency_rates",
        python_callable=update_currency_rates,
    )