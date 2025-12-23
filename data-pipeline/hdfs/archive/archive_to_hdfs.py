from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from datetime import datetime, timedelta
import sys

spark = (
    SparkSession.builder
    .appName("PostgresToHDFS_Archiving")
    .getOrCreate()
)

# 2. 날짜 설정 (오늘로부터 1년 전)
target_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')

def archive_table(table_name):
    print(f"--- Starting Archive: {table_name} (Older than {target_date}) ---")
    
    # 3. PostgreSQL에서 데이터 읽기
    jdbc_url = "jdbc:postgresql://db:5432/travellens"
    df = spark.read \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", f"(SELECT * FROM {table_name} WHERE published_at < '{target_date}') as temp") \
        .option("user", "travellens") \
        .option("password", "2049") \
        .option("driver", "org.postgresql.Driver") \
        .load()

    # 데이터가 있는지 확인
    if df.count() > 0:
        # 4. HDFS에 저장 (국가 iso2별로 파티셔닝하여 저장하면 나중에 조회하기 좋습니다)
        hdfs_path = f"hdfs://namenode:9000/archive/{table_name}"
        df.write \
            .mode("append") \
            .partitionBy("iso2") \
            .parquet(hdfs_path)
        
        print(f"✅ Success: {table_name} data moved to HDFS: {hdfs_path}")
        return True
    else:
        print(f"ℹ️ No data to archive for {table_name}")
        return False

# 실행
tables = ["destination_blog", "destination_news"]
for table in tables:
    archive_table(table)

spark.stop()