from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """
    Extra fields alongside Django's built-in User model.

    We reuse Django's built-in `is_active` flag for "inactive" users (Django
    already refuses login for inactive users — no custom logic needed).
    Admin tiers are handled via `is_staff` / `is_superuser` — see
    permissions.py for how the three tiers (user / staff / admin) map to
    those two built-in flags.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    message_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Max number of messages this user can send. Leave empty for unlimited.",
    )
    # Persistent counter, incremented once per accepted message in
    # SendMessageView. Deliberately NOT computed by counting live Message
    # rows — deleting a conversation cascades and deletes its messages too,
    # which would let someone dodge their limit by deleting old
    # conversations and starting fresh ones.
    messages_sent = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Profile({self.user.username})"

    @property
    def message_count(self):
        return self.messages_sent
