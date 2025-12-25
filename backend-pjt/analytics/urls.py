from django.urls import path
from .views import PopularCountryView, CountryPopularityMapView

urlpatterns = [
    path("popular/", PopularCountryView.as_view(), name="popular-countries"),
    path("popularity/map/", CountryPopularityMapView.as_view(), name="popularity-map"),
]
