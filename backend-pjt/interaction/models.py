from django.db import models
from django.utils import timezone
from django.conf import settings
from travel.models import Country

class FavoriteCountry(models.Model):
    """
    사용자 국가 찜 테이블
    - 추천 / 인기 지표 계산에 활용
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites"
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="favorited_by"
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "favorite_country"
        # 한 유저가 같은 나라를 중복 찜하지 못하도록 제한
        unique_together = ("user", "country")


class UserEvent(models.Model):
    """
    사용자 행동 로그
    - Kafka → Flink 집계 대상
    """

    EVENT_TYPES = (
        ("view", "View"),
        ("click", "Click"),
        ("search", "Search"),
        ("favorite", "Favorite"),
        ("dwell", "Dwell"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="events"
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="events"
    )

    # 행동 유형
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)

    # 체류 시간, 클릭 횟수 등 가변 값
    event_value = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "user_event"
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["country", "created_at"]),
            models.Index(fields=["event_type", "created_at"]),
        ]

