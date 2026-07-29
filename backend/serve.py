"""
Runs the Django app via waitress instead of `manage.py runserver`.

Django's built-in dev server is explicitly documented as unsuitable for
production, and it matters a lot here specifically: SendMessageView holds a
streaming HTTP connection open for the full duration of each reply, so
several coworkers chatting at once means several long-lived connections
held open simultaneously — exactly the kind of load the dev server isn't
built to handle well.

Usage (from the backend/ directory, with your venv activated):
    pip install waitress
    python serve.py
"""

import os

import django
from waitress import serve

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from config.wsgi import application  # noqa: E402

if __name__ == "__main__":
    # threads: how many concurrent requests waitress can actively handle at
    # once. Each active streaming chat reply occupies one thread for its
    # whole duration, so this needs enough headroom for your real concurrent
    # usage, not your total user count (1000 registered users chatting a
    # handful at a time only needs enough threads for that handful, with
    # some buffer for growth).
    serve(application, host="0.0.0.0", port=8000, threads=32)