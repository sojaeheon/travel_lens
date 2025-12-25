from django.urls import path
from .views import CountryInsightView, TravelAlertListView

urlpatterns = [
    path("insights/country", CountryInsightView.as_view()),
    path("alerts", TravelAlertListView.as_view()),
]
