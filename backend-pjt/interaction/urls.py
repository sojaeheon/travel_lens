from django.urls import path

from .views import (
    UserEventCreateView,
    CountryFavoriteStatusAPIView,
    FavoriteCountryListView
)

urlpatterns = [
    path("logs/", UserEventCreateView.as_view(), name="user-event-logs"),
    path("countries/<str:iso2>/favorite/", CountryFavoriteStatusAPIView.as_view(), name="country-favorite-status"),
    path("favorites/", FavoriteCountryListView.as_view(), name="my-favorite-countries"),
]
