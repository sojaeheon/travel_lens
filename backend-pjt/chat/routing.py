from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # ws://localhost:8000/ws/chat/global/ 경로로 접속하게 설정
    re_path(r'ws/chat/global/$', consumers.ChatConsumer.as_asgi()),
]