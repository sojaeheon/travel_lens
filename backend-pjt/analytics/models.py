from django.db import models
from django.utils import timezone
from accounts.models import User
from travel.models import Country


class CountryPopularity(models.Model):
    """
    국가 인기도 집계 결과
    - Flink 스트리밍 결과 저장
    """

    WINDOW_TYPES = (
        ("hourly", "Hourly"),
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="popularity"
    )

    # 집계 윈도우 단위
    window_type = models.CharField(max_length=20, choices=WINDOW_TYPES)

    # 종합 인기도 점수
    score = models.DecimalField(max_digits=10, decimal_places=2)

    # 상세 지표
    view_count = models.BigIntegerField()
    favorite_count = models.BigIntegerField()

    calculated_at = models.DateTimeField()

    class Meta:
        db_table = "country_popularity"
        constraints = [
            models.UniqueConstraint(
                fields=["country", "window_type", "calculated_at"],
                name="uniq_country_window_at"
            )
        ]


class Recommendation(models.Model):
    """
    개인화 추천 결과
    - 배치 or 실시간 추천 결과 저장
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recommendations"
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="recommended_to"
    )

    score = models.DecimalField(max_digits=10, decimal_places=2)

    # 추천 사유 (UI 노출용)
    reason = models.CharField(max_length=255)

    generated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "recommendation"
        indexes = [
            models.Index(fields=["user", "generated_at"]),
        ]
