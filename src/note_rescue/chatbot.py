from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from .chat_context import format_context_for_prompt, gather_note_context
from .chat_corrections import format_corrections_for_prompt
from .secrets import get_openai_api_key, load_secrets, secrets_setup_hint

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"

SYSTEM_PROMPT = """You are a helpful memory assistant for the user's personal rescued Notepad++ notes.

Rules:
- Answer ONLY using the provided note excerpts and user corrections. Do not invent facts.
- The user's notes are often messy, abbreviated, or written in a hurry. Use their corrections when provided.
- If the notes do not contain enough information, say clearly that you could not find it in their vault and suggest what to search for or sync.
- When you rely on a note, cite it as `path` (the Path line from the excerpt).
- Be concise and practical — the user has memory difficulties and needs quick orientation to resume work.
- Prefer bullet points for lists of facts, dates, names, or action items.
- If something in the notes looks ambiguous, mention the ambiguity and what the excerpts actually say."""


def _call_openai(messages: list[dict[str, str]]) -> str:
    api_key = get_openai_api_key()
    if not api_key:
        raise RuntimeError(f"OpenAI API key not configured. {secrets_setup_hint()}")

    secrets = load_secrets()
    model = str(secrets.get("openai_model", "gpt-4o-mini"))

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }

    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OPENAI_CHAT_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"OpenAI API error ({exc.code}): {detail[:500]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach OpenAI API: {exc}") from exc

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected OpenAI response: {data!r}") from exc


def ask_vault(
    question: str,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """
    Answer a question using retrieved vault context and optional conversation history.

    history items: {"role": "user"|"assistant", "content": "..."}
    """
    question = question.strip()
    if not question:
        raise ValueError("Question cannot be empty.")

    blocks, hits = gather_note_context(question)
    context_text = format_context_for_prompt(blocks)
    corrections_text = format_corrections_for_prompt()

    user_parts = [f"Question: {question}", "", "Relevant note excerpts:", context_text]
    if corrections_text:
        user_parts.extend(["", corrections_text])

    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        for item in history[-6:]:
            role = item.get("role", "")
            content = item.get("content", "")
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": "\n".join(user_parts)})

    answer = _call_openai(messages)

    return {
        "answer": answer,
        "sources": blocks,
        "hits": hits,
        "note_count": len(blocks),
    }
