from django.urls import path
from search.views import CountrySearchView, CountrySuggestView

urlpatterns = [
    path("countries/", CountrySearchView.as_view()),
    path("autosearch/",CountrySuggestView.as_view())
]
