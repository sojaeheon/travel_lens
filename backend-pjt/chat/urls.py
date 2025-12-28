from django.urls import path
from .views import GlobalChatHistoryView

urlpatterns = [
    # Vue에서 axios.get('/api/chat/history/')로 요청할 주소
    path('history/', GlobalChatHistoryView.as_view(), name='chat-history'),
]