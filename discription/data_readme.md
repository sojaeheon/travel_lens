# 📊 TravelLens Data Pipeline

> 대용량 실시간 데이터 처리 기반 ETL 파이프라인  
> Kafka, Flink, Airflow를 활용한 현대적인 데이터 엔지니어링

---

## 📋 목차

- [파이프라인 아키텍처](#-파이프라인-아키텍처)
- [실시간 처리 (Kafka + Flink)](#-실시간-처리-kafka--flink)
- [배치 처리 (Airflow)](#-배치-처리-airflow)
- [장기 저장소 (HDFS + Spark)](#-장기-저장소-hdfs--spark)
- [설치 및 실행](#-설치-및-실행)
- [모니터링](#-모니터링)

---

## 🏗️ 파이프라인 아키텍처

### 전체 데이터 흐름

```
┌────────────────────────────────────────────────────────────────────┐
│                     실시간 데이터 수집 (5분마다)                     │
│  ┌──────────────────────┐  ┌──────────────────────┐                │
│  │ 네이버 블로그 API    │  │  Google News RSS     │                │
│  └──────────┬───────────┘  └──────────┬───────────┘                │
│             └──────────────┬───────────┘                             │
│                            ▼                                          │
│              ┌─────────────────────────┐                            │
│              │  Kafka Producer        │                            │
│              │ (travel_blog,          │                            │
│              │  travel_news)          │                            │
│              └──────────┬──────────────┘                            │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
        ┌──────────────────┐     ┌──────────────────┐
        │ Kafka Consumer   │     │  사용자 이벤트    │
        │ (travel_blog)    │     │  Kafka Producer  │
        │ (travel_news)    │     │  (user_events)   │
        └─────────┬────────┘     └─────────┬────────┘
                  │                        │
                  ▼                        ▼
        ┌──────────────────┐     ┌──────────────────┐
        │   PostgreSQL     │     │  Flink 처리      │
        │ (blog, news)     │     │ (1시간 윈도우)    │
        └─────────┬────────┘     └─────────┬────────┘
                  │                        │
        ┌─────────▼────────────────────────▼────────┐
        │         Logstash (3분마다)                │
        │  PostgreSQL → Elasticsearch 동기화        │
        └─────────┬────────────────────────┬────────┘
                  │                        │
            ┌─────▼─────┐           ┌─────▼──────┐
            │ blog_index │           │ country    │
            │ news_index │           │ popularity │
            └────────────┘           └────────────┘
                  ▲                        ▲
                  └────────────┬───────────┘
                               │
                        프론트엔드 (Vue.js)
```

### 배치 처리 (Airflow)

```
┌────────────────────────────────────────────────────┐
│         Airflow Scheduler (24시간 운영)             │
├────────────────────────────────────────────────────┤
│  01:00  → 환율 수집 (get_currency_naver.py)       │
│          ↓ 네이버 크롤링                           │
│          ↓ PostgreSQL 저장                         │
│                                                    │
│  02:00  → 여행경보 수집 (get_travel_alert.py)     │
│          ↓ 공공데이터 API                          │
│          ↓ PostgreSQL 저장                         │
│                                                    │
│  03:00  → 항공권 수집 (get_flight_price.py)       │
│          ↓ Amadeus API                            │
│          ↓ PostgreSQL 저장                         │
│                                                    │
│ 일요일   → 아카이브 작업 (archive_pipeline.py)     │
│ 03:00   ↓ 1년 이상 블로그/뉴스 데이터             │
│          ↓ Spark → HDFS 이동                      │
│          ↓ PostgreSQL에서 삭제                     │
└────────────────────────────────────────────────────┘
```

---

## ⚡ 실시간 처리 (Kafka + Flink)

### 1️⃣ 사용자 행동 → 인기도 집계

#### 데이터 흐름
```
Vue.js (사용자 클릭)
    ↓
Django API (/interaction/logs/)
    ↓
UserEvent 테이블 저장
    ↓
Kafka Producer (user_events 토픽)
    ↓
Flink Job (weekly_country_popularity.py)
    │
    ├─ 1시간 텀블링 윈도우로 그룹핑
    ├─ 가중치 계산 (클릭+조회+찜+체류)
    └─ 상위 10개 국가 선출
    ↓
PostgreSQL (country_popularity 테이블)
    ↓
프론트엔드 (TOP 10 리스트)
```

#### Kafka Producer (Django에서)

```python
# backend-pjt/interaction/kafka/kafka_producer.py
from kafka import KafkaProducer
import json
import os
from datetime import datetime

class UserEventProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=[os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    def send_event(self, user_id, event_type, country_code, value=None):
        """사용자 이벤트를 Kafka에 전송"""
        message = {
            'user_id': user_id,
            'event_type': event_type,  # 'click', 'view', 'favorite', 'stay'
            'country_code': country_code,
            'value': value,  # 체류시간 (초) 또는 null
            'timestamp': int(datetime.now().timestamp())
        }
        self.producer.send('user_events', message)
        self.producer.flush()

# 사용 예
producer = UserEventProducer()
producer.send_event(user_id=1, event_type='country_click', country_code='JP')
```

#### Flink 실시간 처리

```python
# data-pipeline/flink/jobs/weekly_country_popularity.py
from pyflink.datastream import StreamExecutionEnvironment, KeyedStream
from pyflink.datastream.window import TumblingEventTimeWindow
from pyflink.datastream.functions import KeyedProcessFunction
import json
from datetime import datetime, timedelta
import psycopg2

class PopularityAggregator(KeyedProcessFunction):
    """1시간 단위로 국가 인기도 계산"""
    
    SCORE_WEIGHTS = {
        'click': 1.0,
        'view': 3.0,
        'favorite': 10.0,
        'stay': 0.2  # 초당 0.2점
    }
    
    def process_element(self, element, ctx):
        """윈도우 종료 시 호출"""
        country, events = element
        
        # 점수 계산
        total_score = 0
        for event in events:
            if event['event_type'] in self.SCORE_WEIGHTS:
                weight = self.SCORE_WEIGHTS[event['event_type']]
                value = event.get('value', 1)
                
                if event['event_type'] == 'stay':
                    total_score += value * weight  # 체류시간 * 0.2
                else:
                    total_score += weight
        
        # PostgreSQL에 저장
        self.save_to_db(country, total_score)
        
        yield (country, total_score)
    
    def save_to_db(self, country, score):
        conn = psycopg2.connect(
            host='db',
            database='travellens',
            user='travellens',
            password='2049'
        )
        cur = conn.cursor()
        
        calculated_at = datetime.now()
        
        cur.execute("""
            INSERT INTO analytics_countrypopularity 
            (country_iso2, popularity_score, calculated_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (country_iso2, calculated_at) DO UPDATE
            SET popularity_score = EXCLUDED.popularity_score
        """, (country, score, calculated_at))
        
        conn.commit()
        cur.close()
        conn.close()

def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    
    # Kafka 소스
    kafka_source = ...
    
    # 이벤트 타임으로 변환
    events = kafka_source.map(lambda x: json.loads(x)) \
        .assign_timestamps_and_watermarks(...)
    
    # 국가별로 1시간 윈도우로 집계
    aggregated = events \
        .key_by(lambda x: x['country_code']) \
        .window(TumblingEventTimeWindow.of(3600 * 1000)) \
        .process(PopularityAggregator())
    
    env.execute("Country Popularity Calculation")

if __name__ == '__main__':
    main()
```

### 2️⃣ 블로그/뉴스 수집

#### Kafka Producer (외부 API 수집)

```python
# data-pipeline/kafka/producer/travel_blog_producer.py
import requests
import json
from kafka import KafkaProducer
from datetime import datetime
import os
import time

class TravelBlogProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=[os.getenv('KAFKA_BROKER', 'kafka:9092')],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.naver_client_id = os.getenv('NAVER_CLIENT_ID')
        self.naver_client_secret = os.getenv('NAVER_CLIENT_SECRET')
    
    def fetch_blogs(self, country_code, keywords):
        """네이버 블로그 API를 통해 블로그 글 수집"""
        headers = {
            'X-Naver-Client-Id': self.naver_client_id,
            'X-Naver-Client-Secret': self.naver_client_secret
        }
        
        for keyword in keywords:
            query = f"{country_code} {keyword}"
            
            try:
                response = requests.get(
                    'https://openapi.naver.com/v1/search/blog.json',
                    params={
                        'query': query,
                        'display': 10,
                        'sort': 'date'
                    },
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    items = response.json().get('items', [])
                    
                    for item in items:
                        message = {
                            'country_code': country_code,
                            'title': item['title'],
                            'link': item['link'],
                            'description': item['description'],
                            'published_at': item['postdate'],
                            'source': 'naver',
                            'collected_at': datetime.now().isoformat()
                        }
                        
                        # Kafka에 전송
                        self.producer.send('travel_blog', message)
                        print(f"Published: {message['title']}")
                        
            except requests.RequestException as e:
                print(f"Error fetching blogs for {keyword}: {e}")
                time.sleep(2)  # Rate limiting
        
        self.producer.flush()

def run_producer():
    """5분마다 실행되는 Producer (스케줄러에서 호출)"""
    producer = TravelBlogProducer()
    
    # 주요 여행지 국가 & 검색 키워드
    countries = {
        'JP': ['여행', '맛집', '추천', '호텔', '숙박', '항공권', '경비', '일정'],
        'TH': ['태국', '방콕', '푸켓', '여행'],
        'VN': ['베트남', '하노이', '호치민'],
    }
    
    for country_code, keywords in countries.items():
        producer.fetch_blogs(country_code, keywords)

if __name__ == '__main__':
    run_producer()
```

#### Kafka Consumer (PostgreSQL 저장)

```python
# data-pipeline/kafka/consumer/travel_blog_consumer.py
from kafka import KafkaConsumer
import json
import psycopg2
from datetime import datetime
import os

class TravelBlogConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'travel_blog',
            bootstrap_servers=[os.getenv('KAFKA_BROKER', 'kafka:9092')],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='travel-blog-consumer',
            auto_offset_reset='latest'
        )
        self.db_connection = self.get_db_connection()
    
    def get_db_connection(self):
        return psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'db'),
            database=os.getenv('POSTGRES_DB', 'travellens'),
            user=os.getenv('POSTGRES_USER', 'travellens'),
            password=os.getenv('POSTGRES_PASSWORD', '2049')
        )
    
    def save_blog(self, blog_data):
        """블로그 정보를 PostgreSQL에 저장"""
        cur = self.db_connection.cursor()
        
        try:
            cur.execute("""
                INSERT INTO content_destinationblog 
                (iso2, title, link, description, published_at, source)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (link) DO NOTHING
            """, (
                blog_data['country_code'],
                blog_data['title'],
                blog_data['link'],
                blog_data['description'],
                blog_data['published_at'],
                blog_data['source']
            ))
            
            self.db_connection.commit()
            print(f"Saved blog: {blog_data['title']}")
            
        except Exception as e:
            print(f"Error saving blog: {e}")
            self.db_connection.rollback()
        finally:
            cur.close()
    
    def start_consuming(self):
        """Kafka 메시지 소비 시작 (무한 루프)"""
        print("Starting Travel Blog Consumer...")
        
        try:
            for message in self.consumer:
                blog_data = message.value
                self.save_blog(blog_data)
                
        except KeyboardInterrupt:
            print("Consumer stopped")
        finally:
            self.consumer.close()
            self.db_connection.close()

if __name__ == '__main__':
    consumer = TravelBlogConsumer()
    consumer.start_consuming()
```

---

## 🗓️ 배치 처리 (Airflow)

### 환율 수집 DAG

```python
# data-pipeline/airflow/dags/currency_rate_update_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.append('/opt/airflow/dags')

from helpers.get_currency_naver import fetch_and_save_currency

default_args = {
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email': ['admin@example.com']
}

dag = DAG(
    'currency_rate_update_dag',
    default_args=default_args,
    description='매일 새벽 1시에 환율 업데이트',
    schedule_interval='0 1 * * *',  # 매일 01:00
    catchup=False
)

def fetch_currencies():
    """네이버 환율 데이터 수집 및 저장"""
    fetch_and_save_currency()

# 작업 정의
fetch_task = PythonOperator(
    task_id='fetch_currency_rates',
    python_callable=fetch_currencies,
    dag=dag
)

fetch_task
```

### 환율 수집 Helper

```python
# data-pipeline/airflow/dags/helpers/get_currency_naver.py
import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime
import os
import time

def fetch_and_save_currency():
    """네이버 환율 정보 크롤링 및 PostgreSQL 저장"""
    
    db_conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'db'),
        database=os.getenv('POSTGRES_DB', 'travellens'),
        user=os.getenv('POSTGRES_USER', 'travellens'),
        password=os.getenv('POSTGRES_PASSWORD', '2049')
    )
    cur = db_conn.cursor()
    
    # 주요 환율 정보 수집 URL (동적으로 구성)
    currencies = {
        'JP': 'JPY',   # 일본 엔
        'TH': 'THB',   # 태국 바트
        'VN': 'VND',   # 베트남 동
        'US': 'USD',   # 미국 달러
        'EU': 'EUR',   # 유로
    }
    
    for iso2, currency_code in currencies.items():
        try:
            # 네이버 환율 API 호출 (예시)
            response = requests.get(
                f'https://finance.naver.com/marketindex/exchangeDetail.naver',
                params={'query': currency_code},
                timeout=10
            )
            
            if response.status_code == 200:
                # HTML 파싱
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 환율 정보 추출 (셀렉터는 실제 HTML 구조에 따라 조정)
                rate_element = soup.select_one('.exch_rate')
                
                if rate_element:
                    rate = float(rate_element.text.strip().replace(',', ''))
                    
                    # PostgreSQL에 저장
                    cur.execute("""
                        INSERT INTO travel_currency 
                        (iso2, currency_code, currency_krw_unit, recorded_date)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (iso2, recorded_date) DO UPDATE
                        SET currency_krw_unit = EXCLUDED.currency_krw_unit
                    """, (iso2, currency_code, rate, datetime.now().date()))
                    
                    db_conn.commit()
                    print(f"Saved: {iso2} {currency_code} = {rate}")
            
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"Error fetching currency for {iso2}: {e}")
    
    cur.close()
    db_conn.close()
    print("Currency update completed")
```

### 아카이브 파이프라인

```python
# data-pipeline/airflow/dags/archive_pipeline.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2024, 1, 1),
    'retries': 1
}

dag = DAG(
    'archive_pipeline',
    default_args=default_args,
    description='주 1회 오래된 데이터 아카이브',
    schedule_interval='0 3 * * 0',  # 매주 일요일 03:00
    catchup=False
)

# Spark 아카이브 작업
spark_archive = BashOperator(
    task_id='spark_archive_old_data',
    bash_command="""
        spark-submit \
        --master local \
        --driver-memory 2g \
        --executor-memory 2g \
        /data-pipeline/hdfs/archive/archive_to_hdfs.py
    """,
    dag=dag
)

spark_archive
```

### Spark 아카이브 작업

```python
# data-pipeline/hdfs/archive/archive_to_hdfs.py
from pyspark.sql import SparkSession
from datetime import datetime, timedelta
import os

def archive_to_hdfs():
    """1년 이상 된 블로그/뉴스를 HDFS로 이동"""
    
    spark = SparkSession.builder \
        .appName("ArchiveOldData") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .getOrCreate()
    
    # PostgreSQL에서 1년 이전 데이터 읽기
    one_year_ago = (datetime.now() - timedelta(days=365)).date()
    
    # 블로그 데이터 아카이브
    blog_df = spark.read \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://db:5432/travellens") \
        .option("dbtable", """
            (SELECT * FROM content_destinationblog 
             WHERE published_at < '{}') as blogs
        """.format(one_year_ago)) \
        .option("user", "travellens") \
        .option("password", "2049") \
        .load()
    
    # 국가별 파티셔닝으로 HDFS에 저장
    blog_df.write \
        .partitionBy("iso2") \
        .mode("append") \
        .parquet("hdfs://namenode:9000/archive/blogs")
    
    # 뉴스 데이터 아카이브
    news_df = spark.read \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://db:5432/travellens") \
        .option("dbtable", """
            (SELECT * FROM content_destinationnews 
             WHERE published_at < '{}') as news
        """.format(one_year_ago)) \
        .option("user", "travellens") \
        .option("password", "2049") \
        .load()
    
    news_df.write \
        .partitionBy("iso2") \
        .mode("append") \
        .parquet("hdfs://namenode:9000/archive/news")
    
    print("✅ Archive to HDFS completed")
    
    # PostgreSQL에서 아카이브된 데이터 삭제
    import psycopg2
    
    conn = psycopg2.connect(
        host='db',
        database='travellens',
        user='travellens',
        password='2049'
    )
    cur = conn.cursor()
    
    cur.execute(f"""
        DELETE FROM content_destinationblog 
        WHERE published_at < '{one_year_ago}'
    """)
    
    cur.execute(f"""
        DELETE FROM content_destinationnews 
        WHERE published_at < '{one_year_ago}'
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("✅ Old data deleted from PostgreSQL")

if __name__ == '__main__':
    archive_to_hdfs()
```

---

## 🚀 설치 및 실행

### Docker Compose로 실행

```bash
# 전체 데이터 파이프라인 시작
docker-compose up -d kafka zookeeper flink-jobmanager flink-taskmanager airflow-webserver airflow-scheduler

# 로그 확인
docker-compose logs -f kafka
docker-compose logs -f flink-jobmanager
docker-compose logs -f airflow-webserver
```

### Kafka 토픽 생성

```bash
# Kafka 컨테이너 접속
docker-compose exec kafka bash

# 토픽 생성
kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic user_events \
  --partitions 3 \
  --replication-factor 1

kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic travel_blog \
  --partitions 1 \
  --replication-factor 1

kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic travel_news \
  --partitions 1 \
  --replication-factor 1

# 토픽 확인
kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Flink 작업 배포

```bash
# Flink 컨테이너 접속
docker-compose exec flink-jobmanager bash

# Python 작업 제출
/opt/flink/bin/flink run \
  -py /opt/flink/jobs/weekly_country_popularity.py

# 실행 중인 작업 확인
curl http://localhost:8081/api/v1/jobs
```

### Airflow 스케줄러 시작

```bash
# Airflow WebUI 접속
# http://localhost:8081

# 환경 변수 설정 (Airflow)
export AIRFLOW_HOME=/opt/airflow
export AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags
export AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql://airflow:airflow@postgres:5432/airflow

# DAG 확인
docker-compose exec airflow-webserver \
  airflow dags list
```

---

## 📊 모니터링

### Kafka 메시지 모니터링

```bash
# 토픽의 메시지 수 확인
docker-compose exec kafka \
  kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group travel-blog-consumer \
  --describe

# 특정 토픽의 메시지 소비
docker-compose exec kafka \
  kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic user_events \
  --from-beginning
```

### Flink 모니터링

```
WebUI: http://localhost:8081

- Dashboard: 전체 상태
- JobGraph: 작업 플로우 시각화
- TaskManagers: 작업자 상태
- Logs: 상세 로그
```

### Airflow 모니터링

```
WebUI: http://localhost:8081

- DAGs: 모든 파이프라인 목록
- Runs: 실행 이력
- Logs: 각 작업의 로그
- Admin: 연결, 변수, 설정
```

### PostgreSQL 데이터 확인

```bash
# 인기도 데이터 확인
docker-compose exec db psql -U travellens -d travellens -c "
  SELECT country_iso2, popularity_score, ranking, calculated_at
  FROM analytics_countrypopularity
  ORDER BY calculated_at DESC, ranking ASC
  LIMIT 10;
"

# 사용자 이벤트 로그 확인
docker-compose exec db psql -U travellens -d travellens -c "
  SELECT event_type, country_iso2, COUNT(*) as count
  FROM interaction_userevent
  GROUP BY event_type, country_iso2
  ORDER BY count DESC;
"
```

---

## 🔧 트러블슈팅

### Kafka 연결 실패

```bash
# Kafka 상태 확인
docker-compose ps kafka

# 로그 확인
docker-compose logs kafka

# Zookeeper 상태 확인
docker-compose logs zookeeper
```

### Flink 작업 실패

```bash
# TaskManager 로그 확인
docker-compose logs flink-taskmanager

# 작업 재제출
docker-compose exec flink-jobmanager bash
/opt/flink/bin/flink list
/opt/flink/bin/flink cancel <JOB_ID>
```

### Airflow DAG 실행 안됨

```bash
# DAG 파싱 오류 확인
docker-compose exec airflow-webserver \
  airflow dags list-runs --dag-id currency_rate_update_dag

# 작업 상태 확인
docker-compose exec airflow-webserver \
  airflow tasks list currency_rate_update_dag
```

---

**📊 TravelLens Data Pipeline - 데이터의 흐름을 설계하다**
