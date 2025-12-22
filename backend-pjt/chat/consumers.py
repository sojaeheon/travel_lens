import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import GlobalChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    # 1. WebSocket 연결 시 호출
    async def connect(self):
        # 방 이름을 'global_chat'으로 고정 (단일 채팅창)
        self.room_group_name = 'global_chat'

        # Redis 그룹에 현재 채널 추가
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # 연결 수락
        await self.accept()

    # 2. 연결 해제 시 호출
    async def disconnect(self, close_code):
        # Redis 그룹에서 현재 채널 제거
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 3. 클라이언트(Vue)로부터 메시지를 받았을 때 호출
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        
        # 현재 접속한 유저 정보 가져오기 (JWT 미들웨어 적용 시 scope['user']에 유저 객체 존재)
        user = self.scope.get('user')

        if not user or user.is_anonymous:
            # 비로그인 유저인 경우 (테스트 시에는 익명 유저 허용 가능하나 실제 운영 시 제한 필요)
            user_nickname = "Anonymous"
        else:
            # 모델에 nickname 필드가 있다면 사용, 없으면 email 사용
            user_nickname = getattr(user, 'nickname', user.email)

        # 1) DB에 메시지 저장 (비동기 함수 호출)
        if user and not user.is_anonymous:
            await self.save_message(user, message)

        # 2) 그룹 전체에 메시지 전송 (브로드캐스팅)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',  # 아래 정의한 chat_message 메서드를 호출함
                'message': message,
                'user': user_nickname,
            }
        )

    # 4. Redis 그룹에서 메시지를 보낼 때 (실제 클라이언트에게 전송)
    async def chat_message(self, event):
        message = event['message']