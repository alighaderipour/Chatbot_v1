from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import AppSettings, UserProfile


class Command(BaseCommand):
    help = (
        "Manually resets every user's message count to 0 right now, and "
        "marks today as done (so the automatic scheduler won't also reset "
        "later today). Useful if the reset was missed — e.g. the server "
        "was down when the configured daily_reset_time passed."
    )

    def handle(self, *args, **options):
        count = UserProfile.objects.update(messages_sent=0)
        settings_row = AppSettings.load()
        settings_row.last_reset_date = timezone.localdate()
        settings_row.save(update_fields=["last_reset_date"])
        self.stdout.write(self.style.SUCCESS(f"Reset message count for {count} user(s)."))
