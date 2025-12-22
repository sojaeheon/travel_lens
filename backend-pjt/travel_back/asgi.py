"""
ASGI config for travel_back project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_back.settings')

# 1. 일단 HTTP 전용 ASGI application을 가져옵니다.
django_asgi_app = get_asgi_application()

# 2. 프로토콜에 따라 분기 처리를 해주는 Router를 설정합니다.
application = ProtocolTypeRouter({
    # 일반적인 HTTP 요청은 여기서 처리
    "http": django_asgi_app,
    
    # WebSocket 요청은 여기서 처리
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})