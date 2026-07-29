from django.urls import path

from .views import (
    ConversationDetailView,
    ConversationListCreateView,
    SendMessageView,
)

urlpatterns = [
    path("conversations/", ConversationListCreateView.as_view(), name="conversation-list"),
    path("conversations/<uuid:pk>/", ConversationDetailView.as_view(), name="conversation-detail"),
    path(
        "conversations/<uuid:pk>/messages/",
        SendMessageView.as_view(),
        name="conversation-send-message",
    ),
]