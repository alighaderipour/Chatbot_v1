from django.http import StreamingHttpResponse
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .llm_client import build_messages, stream_chat_completion
from .models import Conversation, Message
from .serializers import (
    ConversationDetailSerializer,
    ConversationListSerializer,
    SendMessageSerializer,
)

SYSTEM_PROMPT = "You are a helpful internal company assistant."


class ConversationListCreateView(generics.ListCreateAPIView):
    """GET: list the current user's conversations. POST: start a new one."""

    serializer_class = ConversationListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET: full conversation with message history. PATCH: rename (title only — id/timestamps/messages stay read-only). DELETE: remove it."""

    serializer_class = ConversationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)


class SendMessageView(APIView):
    """
    POST /api/conversations/<uuid:pk>/messages/  { "content": "..." }

    Saves the user's message, streams the model's reply back chunk by
    chunk (so the frontend can render it like ChatGPT), then saves the
    complete assistant reply once streaming finishes.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            conversation = Conversation.objects.get(pk=pk, user=request.user)
        except Conversation.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_content = serializer.validated_data["content"]

        Message.objects.create(
            conversation=conversation, role=Message.Role.USER, content=user_content
        )

        history = list(conversation.messages.all())
        messages_payload = build_messages(history, system_prompt=SYSTEM_PROMPT)

        def event_stream():
            full_reply = []
            for chunk in stream_chat_completion(messages_payload):
                full_reply.append(chunk)
                yield chunk
            Message.objects.create(
                conversation=conversation,
                role=Message.Role.ASSISTANT,
                content="".join(full_reply),
            )
            conversation.save(update_fields=["updated_at"])

        response = StreamingHttpResponse(event_stream(), content_type="text/plain")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"  # needed if you later put nginx in front
        return response