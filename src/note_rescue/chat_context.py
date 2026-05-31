from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .paths import VAULT_DIR
from .search import search_notes, strip_frontmatter
from .secrets import load_secrets


def _truncate(text: str, max_chars: int) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def _extract_search_queries(question: str) -> list[str]:
    """Build one or more keyword queries from a natural-language question."""
    question = question.strip()
    if not question:
        return []

    queries = [question]

    # Drop common question words for a second, keyword-focused pass.
    stop = {
        "what", "when", "where", "who", "why", "how", "did", "do", "does",
        "was", "were", "is", "are", "am", "the", "a", "an", "my", "me",
        "i", "about", "for", "to", "of", "in", "on", "at", "any", "some",
        "tell", "find", "remember", "know", "working", "work", "notes",
    }
    words = [w for w in re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", question.lower()) if w not in stop]
    if len(words) >= 2:
        keyword_query = " ".join(words[:12])
        if keyword_query.lower() != question.lower():
            queries.append(keyword_query)

    return queries


def gather_note_context(question: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Retrieve vault notes relevant to a question using existing keyword search.

    Returns (context_blocks, search_hits) where each block has rel_path, title, excerpt.
    """
    secrets = load_secrets()
    max_notes = int(secrets.get("chat_max_notes", 10))
    max_chars = int(secrets.get("chat_max_chars_per_note", 6000))

    seen_paths: set[str] = set()
    hits: list[dict[str, Any]] = []

    for query in _extract_search_queries(question):
        for hit in search_notes(query, limit=30):
            path = hit["path"]
            if path in seen_paths:
                continue
            seen_paths.add(path)
            hits.append(hit)

    hits.sort(
        key=lambda x: (x.get("phrase_match"), x.get("all_terms_match"), x.get("score", 0)),
        reverse=True,
    )
    hits = hits[: max(max_notes * 2, 20)]

    blocks: list[dict[str, Any]] = []

    for hit in hits:
        if len(blocks) >= max_notes:
            break

        path = Path(hit["path"])
        if not path.exists():
            continue

        try:
            raw = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        body = strip_frontmatter(raw)
        excerpt = _truncate(body, max_chars)

        blocks.append({
            "rel_path": hit["rel_path"],
            "title": hit.get("title", path.stem),
            "excerpt": excerpt,
            "score": hit.get("score", 0),
            "path": str(path),
        })

    return blocks, hits


def format_context_for_prompt(blocks: list[dict[str, Any]]) -> str:
    if not blocks:
        return "(No matching notes were found in the vault for this question.)"

    parts = []
    for i, block in enumerate(blocks, 1):
        parts.append(
            f"--- Note {i}: {block['title']} ---\n"
            f"Path: {block['rel_path']}\n"
            f"{block['excerpt']}"
        )
    return "\n\n".join(parts)
