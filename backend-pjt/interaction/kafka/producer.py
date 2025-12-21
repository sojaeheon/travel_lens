import json
from kafka import KafkaProducer
from django.conf import settings

producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# ===========================
# 사용자 이벤트 전송 프로듀서
# ===========================
def send_user_event(event: dict):
    producer.send(
        topic="user-events",
        value=event
    )
