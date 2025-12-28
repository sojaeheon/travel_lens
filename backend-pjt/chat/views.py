from rest_framework import generics
from .models import GlobalChatMessage
from .serializers import GlobalChatMessageSerializer
from rest_framework.pagination import CursorPagination

# 스크롤을 위로 올릴 때 유용한 Cursor 기반 페이지네이션
class ChatPagination(CursorPagination):
    page_size = 30
    ordering = '-created_at'

class GlobalChatHistoryView(generics.ListAPIView):
    queryset = GlobalChatMessage.objects.all().select_related('sender')
    serializer_class = GlobalChatMessageSerializer
    pagination_class = None