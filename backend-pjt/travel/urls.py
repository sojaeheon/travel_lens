from django.urls import path
from .views import CountryInsightView, TravelAlertListView, ExchangeRateListView

urlpatterns = [
    path("insights/country", CountryInsightView.as_view()),
    path("alerts", TravelAlertListView.as_view()),
    path("exchange", ExchangeRateListView.as_view()),
]
