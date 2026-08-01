import os
import sys

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        # `manage.py runserver`'s autoreloader spawns a parent + child
        # process; without this guard the scheduler would start twice in
        # dev (RUN_MAIN is only set in the reloaded child). Running via
        # `serve.py` (waitress, production) or any other management command
        # never has "runserver" in argv, so this check passes straight
        # through and starts it normally.
        if "runserver" not in sys.argv or os.environ.get("RUN_MAIN") == "true":
            from .scheduler import start_scheduler

            start_scheduler()
