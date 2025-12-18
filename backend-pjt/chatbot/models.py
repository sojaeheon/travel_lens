from django.db import models
from django.utils import timezone
from accounts.models import User


class ChatbotConversation(models.Model):
    """
    챗봇 대화 세션
    - 이전 대화 컨텍스트 유지용
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chatbot_conversations"
    )

    started_at = models.DateTimeField(default=timezone.now)

    # 최근 메시지 시각 (세션 재사용 판단)
    last_message_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "chatbot_conversation"


class ChatbotMessage(models.Model):
    """
    챗봇 대화 메시지
    """

    ROLE_TYPES = (
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
    )

    conversation = models.ForeignKey(
        ChatbotConversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    # 메시지 주체
    role = models.CharField(max_length=20, choices=ROLE_TYPES)

    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "chatbot_message"
