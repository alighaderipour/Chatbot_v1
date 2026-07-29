"""
Thin client for a locally running llama.cpp server (llama-server), which
exposes an OpenAI-compatible /v1/chat/completions endpoint.

Django never loads the .gguf file itself — llama-server does that once,
and every request from every one of your 1000 users just makes an HTTP
call here. This is what lets you serve many users off one loaded model.
"""

import json
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

LLAMA_SERVER_URL = getattr(settings, "LLAMA_SERVER_URL", "http://127.0.0.1:8080")


def build_messages(conversation_messages, system_prompt=None):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    for m in conversation_messages:
        messages.append({"role": m.role, "content": m.content})
    return messages


def stream_chat_completion(messages, temperature=0.7, max_tokens=-1):
    """
    Streams text chunks from llama-server as they're generated, instead of
    waiting for the full reply. Yields plain text pieces.

    max_tokens=-1 tells llama-server to keep generating until the model
    naturally stops (or the context window fills up) instead of being cut
    off at an arbitrary length. The real ceiling is still your `-c` context
    size in llama-server — see the note below.
    """
    payload = {
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }
    with requests.post(
        f"{LLAMA_SERVER_URL}/v1/chat/completions",
        json=payload,
        stream=True,
        timeout=600,
    ) as resp:
        resp.raise_for_status()
        # requests guesses the response encoding from headers when llama-server
        # doesn't send an explicit charset, and that guess often lands on
        # ISO-8859-1 — which silently mangles any non-ASCII text (Persian,
        # Arabic, emoji, etc.) into mojibake. Force UTF-8 explicitly instead
        # of trusting the guess.
        resp.encoding = "utf-8"
        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue
            data = line[len("data:"):].strip()
            if data == "[DONE]":
                break

            try:
                chunk = json.loads(data)
            except json.JSONDecodeError:
                logger.warning("Skipping unparseable SSE line from llama-server: %r", data)
                continue

            if "error" in chunk:
                # llama-server reported a real failure (busy slot, context
                # overflow, etc.) — surface it as an exception instead of
                # silently yielding nothing. Silently swallowing this used to
                # result in an empty assistant message getting saved, which
                # then confused later turns (the model would try to "catch
                # up" on the unanswered question much later in the chat).
                logger.error("llama-server returned an error: %s", chunk["error"])
                raise RuntimeError(f"llama-server error: {chunk['error']}")

            try:
                delta = chunk["choices"][0]["delta"].get("content")
            except (KeyError, IndexError):
                logger.warning("Unexpected chunk shape from llama-server: %r", chunk)
                continue

            if delta:
                yield delta