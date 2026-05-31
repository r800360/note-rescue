from __future__ import annotations

import json
from typing import Any

from .chat_context import format_context_for_prompt, gather_note_context
from .chatbot import _call_openai
from .secrets import get_openai_api_key, secrets_setup_hint
from .site_content import load_profile, load_source_snippets, save_draft
from .site_redact import redact_text

SITE_DRAFT_PROMPT = """You draft PUBLIC personal website content from private note excerpts.

STRICT privacy rules — violating these is worse than leaving a section empty:
- Do NOT include: email addresses, phone numbers, home addresses, student IDs (A########),
  grades, medical/mental health, private mentor/scholar evaluations, drama about individuals,
  or other people's full names unless they are famous public figures.
- Paraphrase; do not copy long verbatim chunks from notes.
- If a note is ambiguous or looks private, skip it or add a short item to draft_notes asking the user to verify.
- You MAY include: research areas, project themes, public values, interests across math/physics/engineering/CS,
  paper or book titles the user is reading (no paywalled PDF paths), inspirational quotes WITHOUT attributing
  private third parties unless clearly public.
- Write for two audiences: recruiters (skills, projects, clarity) and UCSD community (approachable, curious).
- Tone: warm, lightweight, confident — not corporate buzzword soup.

Output ONLY valid JSON with this schema (no markdown fences):
{
  "name": "string",
  "tagline": "string",
  "location_public": "string",
  "about": "2-4 short paragraphs, hiring + general intro",
  "values": ["string", ...],
  "quotes": [{"text": "string", "context": "optional one line"}],
  "projects": [{"title": "string", "summary": "string", "tags": ["string"]}],
  "reading": [{"title": "string", "why": "one line why it matters to you"}],
  "interests": ["math", "physics", ...],
  "links": [{"label": "string", "url": "https://..."}],
  "draft_notes": ["things the user must verify before publishing"]
}"""


FOCUS_QUERIES: dict[str, list[str]] = {
    "about": ["about me bio introduction background", "who am I career goals"],
    "values": ["values principles what I stand for philosophy"],
    "projects": ["project research engineering build", "working on implementation"],
    "quotes": ["quote motto inspiration favorite saying"],
    "reading": ["reading paper book article literature review", "research paper studying"],
    "interests": ["math physics engineering computer science interest"],
    "all": [
        "about me introduction",
        "projects research engineering",
        "values principles",
        "reading papers books",
        "quotes inspiration",
    ],
}


def _gather_context_for_focus(focus: str, extra_query: str = "") -> str:
    focus = (focus or "all").lower()
    queries = list(FOCUS_QUERIES.get(focus, FOCUS_QUERIES["all"]))
    if extra_query.strip():
        queries.insert(0, extra_query.strip())

    seen: set[str] = set()
    blocks: list[dict[str, Any]] = []

    for q in queries:
        note_blocks, _ = gather_note_context(q)
        for block in note_blocks:
            path = block.get("path", "")
            if path in seen:
                continue
            seen.add(path)
            blocks.append(block)
            if len(blocks) >= 12:
                break
        if len(blocks) >= 12:
            break

    parts = [format_context_for_prompt(blocks)]
    sources = load_source_snippets()
    if sources:
        parts.append("Optional files the user placed in site/sources/:\n" + sources)
    return "\n\n".join(parts)


def draft_site_content(focus: str = "all", extra_query: str = "") -> dict[str, Any]:
    if not get_openai_api_key():
        raise RuntimeError(f"OpenAI API key not configured. {secrets_setup_hint()}")

    profile = load_profile()
    context = _gather_context_for_focus(focus, extra_query)

    profile_json = json.dumps(profile, indent=2, ensure_ascii=False)
    sections = profile.get("include_sections", ["about", "values", "projects", "quotes", "reading", "interests"])
    never = profile.get("never_include", [])

    user_msg = (
        f"Focus for this draft: {focus}\n"
        f"Sections to emphasize: {', '.join(sections)}\n"
        f"Never include: {', '.join(never) if never else '(see system rules)'}\n"
        f"User profile seed (override draft only where profile is explicit):\n{profile_json}\n\n"
        f"Note excerpts and optional sources:\n{context}"
    )

    raw = _call_openai([
        {"role": "system", "content": SITE_DRAFT_PROMPT},
        {"role": "user", "content": user_msg},
    ])

    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

    try:
        content = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Model did not return valid JSON. First 400 chars:\n{raw[:400]}") from exc

    if not isinstance(content, dict):
        raise RuntimeError("Model returned non-object JSON.")

    text = json.dumps(content, ensure_ascii=False)
    text = redact_text(text)
    content = json.loads(text)

    return content
