from django.urls import path
from .views import UserEventCreateView, CountryFavoriteStatusAPIView, FavoriteCountriesAPIView

urlpatterns = [
    # 사용자 행동 로그 수집
    path("logs/", UserEventCreateView.as_view()),
    path("countries/<str:iso2>/favorite/",CountryFavoriteStatusAPIView.as_view()),
    path("favorites/", FavoriteCountriesAPIView.as_view()),
]
