from django.db import models
from django.utils import timezone
from django.conf import settings


class GlobalChatMessage(models.Model):
    """
    글로벌 채팅 메시지
    - 방은 1개, 메시지만 저장
    """

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="global_messages"
    )

    content = models.TextField()

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "global_chat_message"
