from django.urls import path
from .views import (
    RagChatAPIView,
    ChatbotHistoryAPIView,
    ChatbotConversationListAPIView,
    ChatbotConversationDeleteAPIView,
    ChatbotConversationClearAPIView,
)

urlpatterns = [
    path("query/", RagChatAPIView.as_view(), name="chatbot-query"),
    path("history/", ChatbotHistoryAPIView.as_view(), name="chatbot-history"),
    path("conversations/", ChatbotConversationListAPIView.as_view(), name="chatbot-conversations"),
    path(
        "conversations/<int:conversation_id>/",
        ChatbotConversationDeleteAPIView.as_view(),
        name="chatbot-conversation-delete",
    ),
    path("conversations/clear/", ChatbotConversationClearAPIView.as_view(), name="chatbot-conversation-clear"),
]
