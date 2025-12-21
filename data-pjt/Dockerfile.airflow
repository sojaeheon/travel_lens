FROM apache/airflow:2.10.0

USER root

# 1. Java 설치 (Spark 실행 필수)
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow

# 2. 필수 라이브러리 설치 (Airflow 버전이 바뀌지 않도록 제약 조건 추가)
RUN pip install --no-cache-dir \
    "apache-airflow-providers-apache-spark==4.8.1" \
    "pyspark==3.5.0" \
    "amadeus==12.0.0"