from django.db import models
from django.utils import timezone
from django.conf import settings
from travel.models import Country


class FavoriteCountry(models.Model):
    """
    사용자 국가 찜 테이블
    - 추천 시스템
    - 인기 여행지 집계에 활용
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

        # 한 사용자가 같은 나라를 중복 찜하지 못하도록 제한
        unique_together = ("user", "country")


class UserEvent(models.Model):
    """
    사용자 행동 로그 테이블
    - 프론트에서 발생한 모든 행동 이벤트 저장
    - Kafka → Flink → Spark 집계의 원천 데이터
    """

    EVENT_TYPES = (
        ("view", "View"),        # 상세 페이지 열림
        ("click", "Click"),      # 지도/리스트 클릭
        ("search", "Search"),    # 검색
        ("favorite", "Favorite"),# 좋아요
        ("dwell", "Dwell"),      # 체류 시간
    )

    # 로그인한 사용자 (비로그인 사용자는 null 
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,              # ⭐ 익명 로그 허용
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events"
    )

    # 행동 대상 국가
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="events"
    )

    # 행동 유형 (집계 기준)
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPES
    )

    # 체류 시간, 클릭 횟수 등 가변 값
    event_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # 이벤트 발생 시각
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "user_event"

        # 시간 기반 분석을 위한 인덱스
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["country", "created_at"]),
            models.Index(fields=["event_type", "created_at"]),
        ]
