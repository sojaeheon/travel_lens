from django.urls import path
from .views import (
    UserEventCreateView, 
    CountryFavoriteStatusAPIView,
    FavoriteCountryListView  # 새로 추가한 뷰
)

urlpatterns = [
    # 1. 사용자 행동 로그 수집 (찜 토글: country_like_toggle 포함)
    path("logs/", UserEventCreateView.as_view(), name="user-event-logs"),
    
    # 2. 특정 국가 찜 여부 확인 (상세페이지 하트 표시용)
    path("countries/<str:iso2>/favorite/", CountryFavoriteStatusAPIView.as_view(), name="country-favorite-status"),
    
    # 3. 내 찜 목록 전체 조회 (마이페이지용) ⭐ 새로 추가
    path("favorites/", FavoriteCountryListView.as_view(), name="my-favorite-countries"),
]