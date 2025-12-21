from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from travel.models import Country
from .models import UserEvent, FavoriteCountry
from .serializers import UserEventCreateSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# kafka producer 관련 함수
from interaction.kafka.producer import send_user_event

# ⭐ 프론트 이벤트 → DB 이벤트 타입 매핑
# 프론트는 의미 중심, DB는 집계 중심
EVENT_TYPE_MAP = {
    "country_click": "click",
    "country_search_select": "search",
    "country_detail_open": "view",
    "country_detail_stay": "dwell",
    "country_like_toggle": "favorite",
}


class UserEventCreateView(APIView):
    """
    사용자 행동 로그 수집 API
    - 로그인 / 비로그인 모두 허용
    - 추천 / 인기 계산을 위한 원천 데이터 생성
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="사용자 행동 로그 수집",
        operation_description="""
        로그인/비로그인 사용자의 행동 로그를 수집합니다.
        추천 및 인기 여행지 계산을 위한 원천 데이터로 사용됩니다.
        """,
        request_body=UserEventCreateSerializer,
        responses={
            204: "로그 저장 성공",
            400: "잘못된 요청",
        }
    )

    def post(self, request):
        serializer = UserEventCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        raw_event_type = serializer.validated_data["event_type"]
        iso2 = serializer.validated_data["country_code"]
        value = serializer.validated_data.get("value")

        # 2️⃣ 이벤트 타입 매핑 확인
        if raw_event_type not in EVENT_TYPE_MAP:
            return Response(
                {"detail": "Invalid event_type"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3️⃣ 국가 존재 여부 확인
        try:
            country = Country.objects.get(iso2=iso2)
        except Country.DoesNotExist:
            return Response(
                {"detail": "Invalid country_code"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4️⃣ 사용자 판별 (JWT 있으면 user, 없으면 None)
        user = request.user if request.user.is_authenticated else None

        # 5️⃣ user_event PostgreSQL 저장 (🔥 정답 데이터)
        event = UserEvent.objects.create(
            user=user,
            country=country,
            event_type=EVENT_TYPE_MAP[raw_event_type],
            event_value=value
        )

        # 6️⃣ Kafka 발행 (🔥 분석용 스트림)
        try:
            send_user_event({
                "event_id": event.id,
                "user_id": user.id if user else None,
                "country_iso2": country.iso2,
                "event_type": event.event_type,
                "event_value": float(event.event_value) if event.event_value else None,
                "created_at": event.created_at.isoformat(),
            })
        except Exception as e:
            # ⚠️ Kafka 장애 → 서비스는 정상 동작
            print("Kafka send failed:", e)

        # 6️⃣ 좋아요 이벤트면 FavoriteCountry 테이블도 동기화
        if raw_event_type == "country_like_toggle" and user:
            qs = FavoriteCountry.objects.filter(
                user=user,
                country=country
            )

            if qs.exists():
                qs.delete()      # 이미 찜 → 취소
            else:
                FavoriteCountry.objects.create(
                    user=user,
                    country=country
                )                # 없으면 → 찜

        # 7️⃣ 응답 (비동기 로그 → 내용 반환 불필요)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CountryFavoriteStatusAPIView(APIView):
    """
    특정 국가에 대한 찜 상태 조회
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, iso2):
        # 1️⃣ 국가 존재 확인
        try:
            country = Country.objects.get(iso2=iso2)
        except Country.DoesNotExist:
            return Response(
                {"detail": "Invalid country code"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2️⃣ 찜 여부 확인
        is_favorited = FavoriteCountry.objects.filter(
            user=request.user,
            country=country
        ).exists()
        # 3️⃣ 응답
        return Response(
            {"is_favorited": is_favorited},
            status=status.HTTP_200_OK
        )