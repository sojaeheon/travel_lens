from django.urls import path
from .views import UserEventCreateView

urlpatterns = [
    # 사용자 행동 로그 수집
    path("logs/", UserEventCreateView.as_view()),
]
