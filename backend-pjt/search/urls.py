from django.urls import path
from search.views import CountrySearchView, CountrySuggestView, NewsSearchView, BlogSearchView,SearchSuggestView

urlpatterns = [
    path("countries/", CountrySearchView.as_view()),
    path("autosearch/",CountrySuggestView.as_view()),
    path("news/", NewsSearchView.as_view()),
    path("blogs/", BlogSearchView.as_view()),
    # 자동완성
    path("suggest/", SearchSuggestView.as_view()),
]
