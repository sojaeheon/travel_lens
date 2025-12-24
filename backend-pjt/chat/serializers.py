from rest_framework import serializers
from .models import GlobalChatMessage
from django.contrib.auth import get_user_model

User = get_user_model()

class GlobalChatMessageSerializer(serializers.ModelSerializer):
    sender_nickname = serializers.SerializerMethodField()
    sender_email = serializers.ReadOnlyField(source='sender.email')
    
    class Meta:
        model = GlobalChatMessage
        fields = ['id', 'content', 'sender_nickname', 'sender_email', 'created_at']
        read_only_fields = ['created_at']
    
    def get_sender_nickname(self, obj):
        """
        Email에서 @ 앞 부분만 추출
        예: jane@example.com → "jane"
        """
        email = obj.sender.email
        return email.split('@')[0] if email else "사용자"
