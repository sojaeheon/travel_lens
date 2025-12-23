import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import GlobalChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'global_chat'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        print(f"✅ 클라이언트 연결됨")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"⛔ 클라이언트 연결 해제 (코드: {close_code})")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_text = text_data_json.get('message')
        user = self.scope.get('user')

        print(f"\n📨 메시지 수신: {message_text}")
        print(f"👤 user 객체: {user}")
        print(f"👤 is_anonymous: {user.is_anonymous if hasattr(user, 'is_anonymous') else 'N/A'}")
        
        # 유저가 있거나 로그인된 경우 정보 추출, 아니면 익명 처리
        if user and not user.is_anonymous:
            # ⭐ email에서 @ 앞 부분만 추출
            user_email = user.email
            user_nickname = user_email.split('@')[0] if user_email else "사용자"
            print(f"✅ 로그인 사용자: {user_nickname} ({user_email})")
            
            # 로그인 된 경우만 DB 저장
            await self.save_message(user, message_text)
        else:
            user_nickname = "익명 사용자"
            user_email = "anonymous"
            print(f"⚠️  익명 사용자 메시지")

        # 그룹 전체에 알림 (모든 필드 포함)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'user': user_nickname,
                'sender_nickname': user_nickname,
                'sender_email': user_email,
                'created_at': timezone.now().isoformat(),
            }
        )

    async def chat_message(self, event):
        # ✅ 히스토리 API의 필드와 일관성 있게 전송
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user': event['user'],
            'sender_nickname': event.get('sender_nickname', event['user']),
            'sender_email': event['sender_email'],
            'created_at': event['created_at']
        }))

    @database_sync_to_async
    def save_message(self, user, message):
        return GlobalChatMessage.objects.create(
            sender=user,
            content=message
        )
