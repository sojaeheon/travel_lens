from rest_framework import serializers
from .models import GlobalChatMessage
from django.contrib.auth import get_user_model

User = get_user_model()

class GlobalChatMessageSerializer(serializers.ModelSerializer):
    # 보낸 사람의 닉네임을 가져옵니다. (모델에 nickname이 없다면 email이나 username 사용)
    sender_nickname = serializers.ReadOnlyField(source='sender.nickname')
    sender_email = serializers.ReadOnlyField(source='sender.email')
    
    class Meta:
        model = GlobalChatMessage
        fields = ['id', 'content', 'sender_nickname', 'sender_email', 'created_at']
        read_only_fields = ['created_at']