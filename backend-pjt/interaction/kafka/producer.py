import json
import os
from kafka import KafkaProducer

_producer = None


def get_producer():
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=os.getenv(
                "KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"
            ),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            retries=3,
            linger_ms=10,
        )
    return _producer


def send_user_event(data: dict):
    try:
        producer = get_producer()
        producer.send("user_events", data)
    except Exception as e:
        # ❗ Kafka 장애가 서비스 장애로 이어지면 안 됨
        print("Kafka send failed:", e)
