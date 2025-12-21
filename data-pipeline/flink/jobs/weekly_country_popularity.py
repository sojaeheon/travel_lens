from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.window import SlidingEventTimeWindows
from pyflink.datastream.functions import ProcessWindowFunction
from pyflink.common.time import Time
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.typeinfo import Types
from datetime import timedelta, datetime
import json

# Kafka
from pyflink.datastream.connectors.kafka import KafkaSource
from pyflink.common.serialization import SimpleStringSchema

# flink sink 코드
from pyflink.datastream.connectors.jdbc import JdbcSink
from pyflink.common.typeinfo import Types


# ==================================================
# 1️⃣ Flink 실행 환경
# ==================================================
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)  # 초기엔 반드시 1
env.enable_checkpointing(60000)

# ==================================================
# 2️⃣ Kafka Source 설정
# ==================================================
source = KafkaSource.builder() \
    .set_bootstrap_servers("kafka:9092") \
    .set_topics("user_events") \
    .set_group_id("flink-weekly-popularity") \
    .set_value_only_deserializer(SimpleStringSchema()) \
    .build()

stream = env.from_source(
    source,
    WatermarkStrategy
        .for_bounded_out_of_orderness(timedelta(minutes=5))
        .with_timestamp_assigner(
            lambda e, ts: int(json.loads(e)["created_at_ts"])
        ),
    "KafkaUserEventSource"
)


# ==================================================
# 3️⃣ JSON 파싱 + EventTime 추출
# ==================================================
def parse_event(value: str):
    data = json.loads(value)

    return (
        data["country_iso2"],                 # 0
        data["event_type"],                   # 1
        data.get("event_value"),              # 2 (체류시간 등)
        datetime.fromisoformat(data["created_at"])  # 3
    )

parsed = stream.map(
    parse_event,
    output_type=Types.TUPLE([
        Types.STRING(),         # country_iso2
        Types.STRING(),         # event_type
        Types.DOUBLE(),         # event_value (nullable)
        Types.SQL_TIMESTAMP()   # created_at
    ])
)


# ==================================================
# 4️⃣ Watermark (Event Time 기준)
# ==================================================
watermarked = parsed.assign_timestamps_and_watermarks(
    WatermarkStrategy
    .for_bounded_out_of_orderness(timedelta(minutes=5))
    .with_timestamp_assigner(
        lambda e, ts: int(e[3].timestamp() * 1000)
    )
)


# ==================================================
# 5️⃣ Window 집계 로직
# ==================================================
class WeeklyPopularityWindow(ProcessWindowFunction):

    def process(self, key, context, elements, out):
        """
        key: country_iso2
        elements: 해당 국가의 7일간 이벤트들
        """

        view_count = 0
        favorite_count = 0
        score = 0.0

        for e in elements:
            event_type = e[1]
            event_value = e[2] or 0.0

            if event_type == "country_click":
                score += 1

            elif event_type == "country_detail_open":
                view_count += 1
                score += 3

            elif event_type == "country_search_select":
                score += 4

            elif event_type == "country_detail_stay":
                # 체류시간 반영 (상한선)
                score += min(event_value * 0.2, 20)

            elif event_type == "country_like_toggle":
                favorite_count += 1
                score += 10

        out.collect((
            key,                        # country_iso2
            view_count,                 # view_count
            favorite_count,             # favorite_count
            round(score, 2),            # score
            context.window().get_end()  # window_end_time
        ))


# ==================================================
# 6️⃣ Sliding Window (7일 / 10분)
# ==================================================
aggregated = watermarked \
    .key_by(lambda e: e[0]) \
    .window(
        SlidingEventTimeWindows.of(
            Time.days(7),
            Time.minutes(10)
        )
    ) \
    .process(
        WeeklyPopularityWindow(),
        output_type=Types.TUPLE([
            Types.STRING(),         # country_iso2
            Types.LONG(),           # view_count
            Types.LONG(),           # favorite_count
            Types.DOUBLE(),         # score
            Types.SQL_TIMESTAMP()   # calculated_at
        ])
    )


# ==================================================
# 7️⃣ (임시) 결과 확인용 출력
# ==================================================
aggregated.print()

jdbc_sink = JdbcSink.sink(
    sql="""
        INSERT INTO country_popularity (
            country_id,
            window_type,
            score,
            view_count,
            favorite_count,
            calculated_at
        )
        VALUES (
            (SELECT id FROM country WHERE iso2 = ?),
            'weekly',
            ?, ?, ?, ?
        )
        ON CONFLICT (country_id, window_type)
        DO UPDATE SET
            score = EXCLUDED.score,
            view_count = EXCLUDED.view_count,
            favorite_count = EXCLUDED.favorite_count,
            calculated_at = EXCLUDED.calculated_at;
    """,
    setter=lambda ps, t: (
        ps.set_string(1, t[0]),   # country_iso2
        ps.set_double(2, t[3]),   # score
        ps.set_long(3, t[1]),     # view_count
        ps.set_long(4, t[2]),     # favorite_count
        ps.set_timestamp(5, t[4]) # calculated_at
    ),
    jdbc_url="jdbc:postgresql://db:5432/travellens",
    driver_name="org.postgresql.Driver",
    username="travellens",
    password="2049"
)

aggregated.add_sink(jdbc_sink)

env.execute("Weekly Country Popularity To Postgre")
