from django.conf import settings
from django.db import models


class AppSettings(models.Model):
    """
    Singleton row (always pk=1) holding app-wide settings the admin
    controls from the Preferences tab. Only `daily_reset_time` exists for
    now, but this is the natural place to add more org-wide settings later.
    """

    daily_reset_time = models.TimeField(
        default="07:00",
        help_text="Every user's message count resets to 0 at this time, every day.",
    )
    # Tracks the last date the reset actually ran, so the background
    # scheduler (see scheduler.py) doesn't reset twice in the same day if
    # it happens to check more than once after the target time.
    last_reset_date = models.DateField(null=True, blank=True)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"AppSettings(daily_reset_time={self.daily_reset_time})"


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
    # conversations and starting fresh ones. Reset to 0 daily by the
    # background scheduler at AppSettings.daily_reset_time — that's a
    # deliberate, admin-controlled reset, unlike the conversation-deletion
    # case above.
    messages_sent = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Profile({self.user.username})"

    @property
    def message_count(self):
        return self.messages_sent
