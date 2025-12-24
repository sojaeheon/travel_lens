# dags/archive_pipeline.py

from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator
import os

# 환경변수에서 HDFS 아카이브 경로 가져오기
ARCHIVE_PATH = os.getenv("ARCHIVE_PATH", "hdfs://namenode:9000/archive/travel_data")

default_args = {
    'owner': 'travellens',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'weekly_archive_to_hdfs',
    default_args=default_args,
    description='Move data older than 1 year from Postgres to HDFS',
    schedule_interval='0 3 * * 0',  # 매주 일요일 새벽 3시
    catchup=False
) as dag:

    # 1️⃣ Spark 작업: SparkSubmitOperator 대신 BashOperator 사용
    transfer_task = BashOperator(
        task_id="transfer_data_to_hdfs",
        bash_command="""
            spark-submit \
            --master local[*] \
            --deploy-mode client \
            --name archive_to_hdfs \
            --jars /opt/airflow/scripts/lib/postgresql-42.7.5.jar \
            --driver-class-path /opt/airflow/scripts/lib/postgresql-42.7.5.jar \
            /opt/airflow/hdfs/archive/archive_to_hdfs.py \
            {{ params.archive_path }}
        """,
        params={'archive_path': ARCHIVE_PATH},
        dag=dag,
    )

    # 2️⃣ Postgres cleanup: 이동 완료 후 1년 이상 데이터 삭제
    delete_queries = [
        "DELETE FROM destination_blog WHERE published_at < NOW() - INTERVAL '1 year';",
        "DELETE FROM destination_news WHERE published_at < NOW() - INTERVAL '1 year';"
    ]

    cleanup_task = PostgresOperator(
        task_id='delete_old_data_from_postgres',
        postgres_conn_id='travel_postgres',
        sql=delete_queries
    )

    # DAG 의존성 정의
    transfer_task >> cleanup_task
