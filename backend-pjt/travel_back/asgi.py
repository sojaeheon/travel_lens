import os
import django
from django.core.asgi import get_asgi_application

# 1. 환경 변수 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_back.settings')

# 2. Django 초기화 (미들웨어 임포트보다 먼저 실행되어야 에러가 안 남)
django.setup()

# 3. 그 다음 Channels 관련 임포트
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.middlewares import JwtAuthMiddleware
from chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddleware(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})