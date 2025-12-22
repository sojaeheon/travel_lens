from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings

env = StreamExecutionEnvironment.get_execution_environment()
settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
t_env = StreamTableEnvironment.create(env, settings)

# 1️⃣ Kafka Source: 워터마크 정밀도를 TIMESTAMP(3)로 맞춤
t_env.execute_sql("""
CREATE TABLE user_event (
    country_iso2 STRING,
    event_type STRING,
    event_value DOUBLE,
    created_at TIMESTAMP(3),
    proc_time AS PROCTIME(),
    WATERMARK FOR created_at AS created_at 
) WITH (
    'connector' = 'kafka',
    'topic' = 'user_events',
    'properties.bootstrap.servers' = 'kafka:9092',
    'properties.group.id' = 'flink-weekly-popularity-v3', -- 🔥 변경
    'properties.auto.offset.reset' = 'latest',
    'format' = 'json'
)
""")

# 2️⃣ Country Lookup
t_env.execute_sql("""
CREATE TABLE country_lookup (
    iso2 STRING,
    iso3 STRING,
    name_ko STRING,
    name_en STRING,
    continent_name_en STRING,
    continent_name_ko STRING,
    PRIMARY KEY (iso2) NOT ENFORCED
) WITH (
    'connector' = 'jdbc',
    'url' = 'jdbc:postgresql://db:5432/travellens',
    'table-name' = 'country',
    'username' = 'travellens',
    'password' = '2049',
    'lookup.cache.max-rows' = '1000',
    'lookup.cache.ttl' = '1 hour'
)
""")

# 3️⃣ Sink
t_env.execute_sql("""
CREATE TABLE country_popularity_sink (
    window_type STRING,
    score DOUBLE,
    view_count BIGINT,
    favorite_count BIGINT,
    calculated_at TIMESTAMP(3),
    country_id STRING,
    PRIMARY KEY (country_id, window_type) NOT ENFORCED
) WITH (
    'connector' = 'jdbc',
    'url' = 'jdbc:postgresql://db:5432/travellens',
    'table-name' = 'country_popularity',
    'username' = 'travellens',
    'password' = '2049'
)
""")

# 4️⃣ 실행: 데이터 확인을 위해 1분 단위 윈도우로 수정
# 테스트 성공 후 '1 MINUTE'를 '7 DAY'로 바꾸세요.
t_env.execute_sql("""
INSERT INTO country_popularity_sink
SELECT
    'weekly' AS window_type,
    SUM(
        CASE
            WHEN e.event_type = 'click' THEN 1.0
            WHEN e.event_type = 'view' THEN 3.0
            WHEN e.event_type = 'favorite' THEN 10.0
            WHEN e.event_type = 'dwell'
                THEN LEAST(COALESCE(e.event_value, 0.0) * 0.2, 20.0)
            ELSE 0.0
        END
    ) AS score,
    SUM(CASE WHEN e.event_type = 'view' THEN 1 ELSE 0 END) AS view_count,
    SUM(CASE WHEN e.event_type = 'favorite' THEN 1 ELSE 0 END) AS favorite_count,
    TUMBLE_END(e.created_at, INTERVAL '1' HOUR) AS calculated_at,
    c.iso2 AS country_id
FROM user_event AS e
JOIN country_lookup FOR SYSTEM_TIME AS OF e.proc_time AS c
ON e.country_iso2 = c.iso2
GROUP BY
    c.iso2,
    TUMBLE(e.created_at, INTERVAL '1' HOUR)
""")