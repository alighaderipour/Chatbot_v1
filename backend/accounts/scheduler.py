"""
Runs a background job inside the Django/waitress process that checks once a
minute whether it's time for the daily message-count reset, and performs it
exactly once per day.

We use an in-process scheduler (APScheduler) instead of a separate service
like Celery+Redis or an OS-level cron job — this app runs on a single
Windows machine via `waitress`, so a lightweight background thread inside
that same process is simpler to operate than standing up extra
infrastructure just for one daily job.

Caveat worth knowing: if the server happens to be restarted right around
the reset time, that day's reset could be skipped (it'll still run
correctly the next day). For this scale, that's an acceptable tradeoff
against the complexity of a more robust job queue.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone

logger = logging.getLogger(__name__)

_scheduler = None


def _check_and_reset():
    # Imported here, not at module level, so this file can be imported
    # during Django app startup before models are ready.
    from .models import AppSettings, UserProfile

    settings_row = AppSettings.load()
    now = timezone.localtime()

    already_ran_today = settings_row.last_reset_date == now.date()
    if already_ran_today or now.time() < settings_row.daily_reset_time:
        return

    count = UserProfile.objects.update(messages_sent=0)
    settings_row.last_reset_date = now.date()
    settings_row.save(update_fields=["last_reset_date"])
    logger.info("Daily message count reset ran — %s profile(s) reset.", count)


def start_scheduler():
    global _scheduler
    if _scheduler is not None:
        return  # already running — don't start a second one

    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(_check_and_reset, "interval", minutes=1, id="daily_message_reset")
    _scheduler.start()
    logger.info("Message-count reset scheduler started.")
