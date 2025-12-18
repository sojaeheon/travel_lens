from django.urls import path
from accounts.views import RegisterAPIView, LoginAPIView, ChangePasswordAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("change-password/", ChangePasswordAPIView.as_view()),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]