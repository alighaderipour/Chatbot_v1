from django.http import StreamingHttpResponse
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserProfile

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

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if profile.message_limit is not None and profile.message_count >= profile.message_limit:
            return Response(
                {"detail": "You've reached your message limit. Contact an admin to increase it."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_content = serializer.validated_data["content"]

        Message.objects.create(
            conversation=conversation, role=Message.Role.USER, content=user_content
        )
        profile.messages_sent += 1
        profile.save(update_fields=["messages_sent"])

        history = list(conversation.messages.all())
        messages_payload = build_messages(history, system_prompt=SYSTEM_PROMPT)

        def event_stream():
            full_reply = []
            try:
                for chunk in stream_chat_completion(messages_payload):
                    full_reply.append(chunk)
                    yield chunk
            except Exception:
                # If llama-server failed partway through (or immediately),
                # don't silently save an empty message — that used to cause
                # confusing behavior where the model "caught up" on an
                # unanswered question several turns later. Save (and show)
                # a clear error instead, on top of whatever partial text,
                # if any, already streamed to the client before the failure.
                error_text = (
                    "\n\n⚠️ Something went wrong generating a reply. Please try again."
                )
                full_reply.append(error_text)
                yield error_text

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
