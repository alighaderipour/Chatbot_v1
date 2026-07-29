"""
Thin client for a locally running llama.cpp server (llama-server), which
exposes an OpenAI-compatible /v1/chat/completions endpoint.

Django never loads the .gguf file itself — llama-server does that once,
and every request from every one of your 1000 users just makes an HTTP
call here. This is what lets you serve many users off one loaded model.
"""

import json

import requests
from django.conf import settings

LLAMA_SERVER_URL = getattr(settings, "LLAMA_SERVER_URL", "http://127.0.0.1:8080")


def build_messages(conversation_messages, system_prompt=None):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    for m in conversation_messages:
        messages.append({"role": m.role, "content": m.content})
    return messages


def stream_chat_completion(messages, temperature=0.7, max_tokens=1024):
    """
    Streams text chunks from llama-server as they're generated, instead of
    waiting for the full reply. Yields plain text pieces.
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
        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue
            data = line[len("data:"):].strip()
            if data == "[DONE]":
                break
            try:
                chunk = json.loads(data)
                delta = chunk["choices"][0]["delta"].get("content")
                if delta:
                    yield delta
            except (json.JSONDecodeError, KeyError, IndexError):
                continue