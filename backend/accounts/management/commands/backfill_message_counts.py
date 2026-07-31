from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import UserProfile
from chatbot.models import Message


class Command(BaseCommand):
    help = (
        "One-time backfill: sets each user's persistent messages_sent counter "
        "from their existing message history, since the counter used to be "
        "computed live (and reset when conversations were deleted) before "
        "this became a real field. Safe to run more than once."
    )

    def handle(self, *args, **options):
        updated = 0
        for user in User.objects.all():
            historical_count = Message.objects.filter(
                conversation__user=user, role=Message.Role.USER
            ).count()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if profile.messages_sent < historical_count:
                profile.messages_sent = historical_count
                profile.save(update_fields=["messages_sent"])
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Backfilled {updated} user(s)."))
