from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from travel.models import Country
from .models import UserEvent, FavoriteCountry
from .serializers import UserEventCreateSerializer, FavoriteCountrySerializer # 📌 시리얼라이저 추가

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# kafka producer 관련 함수
from interaction.kafka.producer import send_user_event

# ⭐ 프론트 이벤트 → DB 이벤트 타입 매핑
EVENT_TYPE_MAP = {
    "country_click": "click",
    "country_search_select": "search",
    "country_detail_open": "view",
    "country_detail_stay": "dwell",
    "country_like_toggle": "favorite",
}

class FavoriteCountryListView(APIView):
    """
    내 찜 목록 조회 API
    - 로그인한 사용자가 찜한 국가들의 상세 정보(ISO2, 영문명, 한글명)를 반환
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="내 찜 목록 조회",
        operation_description="로그인한 유저가 찜한 국가 리스트를 가져옵니다. Pexels 이미지 검색에 필요한 name_en을 포함합니다.",
        responses={200: FavoriteCountrySerializer(many=True)}
    )
    def get(self, request):
        # 📌 select_related('country')를 사용하여 쿼리 최적화 (Join 실행)
        favorites = FavoriteCountry.objects.filter(
            user=request.user
        ).select_related('country')
        
        serializer = FavoriteCountrySerializer(favorites, many=True)
        return Response(
            {"count": len(serializer.data), "results": serializer.data},
            status=status.HTTP_200_OK
        )


class UserEventCreateView(APIView):
    """
    사용자 행동 로그 수집 API (찜 토글 로직 포함)
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="사용자 행동 로그 수집",
        request_body=UserEventCreateSerializer,
        responses={204: "로그 저장 성공", 400: "잘못된 요청"}
    )
    def post(self, request):
        serializer = UserEventCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        raw_event_type = serializer.validated_data["event_type"]
        iso2 = serializer.validated_data["country_code"]
        value = serializer.validated_data.get("value")

        if raw_event_type not in EVENT_TYPE_MAP:
            return Response({"detail": "Invalid event_type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            country = Country.objects.get(iso2=iso2)
        except Country.DoesNotExist:
            return Response({"detail": "Invalid country_code"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else None

        # 1. UserEvent 로그 저장
        event = UserEvent.objects.create(
            user=user,
            country=country,
            event_type=EVENT_TYPE_MAP[raw_event_type],
            event_value=value
        )

        # 2. Kafka 발행
        try:
            formatted_created_at = event.created_at.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            send_user_event({
                "event_id": event.id,
                "user_id": user.id if user else None,
                "country_iso2": country.iso2,
                "event_type": event.event_type,
                "event_value": float(event.event_value) if event.event_value else None,
                "created_at": formatted_created_at
            })
        except Exception as e:
            print("Kafka send failed:", e)

        # 3. 찜 토글 로직 (중요)
        if raw_event_type == "country_like_toggle" and user:
            qs = FavoriteCountry.objects.filter(user=user, country=country)
            if qs.exists():
                qs.delete() # 이미 있으면 삭제 (Unfavorite)
            else:
                FavoriteCountry.objects.create(user=user, country=country) # 없으면 생성 (Favorite)

        return Response(status=status.HTTP_204_NO_CONTENT)


class CountryFavoriteStatusAPIView(APIView):
    """
    특정 국가에 대한 찜 상태 조회 (상세 페이지 하트 표시용)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, iso2):
        try:
            country = Country.objects.get(iso2=iso2)
        except Country.DoesNotExist:
            return Response({"detail": "Invalid country code"}, status=status.HTTP_400_BAD_REQUEST)

        is_favorited = FavoriteCountry.objects.filter(
            user=request.user,
            country=country
        ).exists()
        return Response({"is_favorited": is_favorited}, status=status.HTTP_200_OK)
