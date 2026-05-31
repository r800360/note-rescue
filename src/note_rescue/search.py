from __future__ import annotations

import re
from pathlib import Path
from typing import List, Dict

from .paths import VAULT_DIR


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3 :].lstrip("\n")
    return text


def note_label(path: Path) -> str:
    stem = path.stem
    parts = stem.split("_", 2)
    if len(parts) >= 2:
        return parts[1].replace("-", " ")
    return stem


def search_notes(query: str, limit: int = 20) -> List[Dict]:
    """
    Search the Markdown vault.

    Ranking priority:
    1. Exact phrase in note body
    2. Exact phrase in filename / path
    3. All query terms present (frequency capped so one common word does not dominate)
    """
    query = query.strip()
    query_terms = [term.lower() for term in query.split() if term.strip()]
    phrase = query.lower()

    if not query_terms:
        return []

    results = []

    for path in VAULT_DIR.rglob("*.md"):
        if path.name == "global_todos.md":
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        body = strip_frontmatter(text)
        body_lower = body.lower()
        path_lower = str(path).lower()
        rel = str(path.relative_to(VAULT_DIR)) if VAULT_DIR in path.parents else str(path)

        term_counts = {term: body_lower.count(term) for term in query_terms}
        matched_terms = [term for term, count in term_counts.items() if count > 0]

        if not matched_terms:
            continue

        all_terms_match = len(matched_terms) == len(query_terms)

        phrase_in_body = body_lower.count(phrase)
        phrase_slug = phrase.replace(" ", "-")
        phrase_in_path = phrase in path_lower or phrase_slug in path_lower

        # Cap per-term hits so "student" x50 does not beat a note with the full phrase once.
        capped_term_score = sum(min(count, 4) for count in term_counts.values())

        score = capped_term_score
        if all_terms_match:
            score += 500
        if phrase_in_path:
            score += 3000
        if phrase_in_body:
            score += 8000 + (phrase_in_body - 1) * 1000

        snippet = make_snippet(body, query_terms, phrase)

        results.append({
            "path": str(path),
            "rel_path": rel,
            "title": note_label(path),
            "score": score,
            "phrase_match": phrase_in_body > 0 or phrase_in_path,
            "all_terms_match": all_terms_match,
            "matched_terms": len(matched_terms),
            "snippet": snippet,
        })

    results.sort(
        key=lambda x: (
            x["phrase_match"],
            x["all_terms_match"],
            x["matched_terms"],
            x["score"],
        ),
        reverse=True,
    )

    return results[:limit]


def make_snippet(text: str, query_terms: list[str], phrase: str = "", radius: int = 140) -> str:
    lowered = text.lower()
    first_pos = None

    if phrase:
        first_pos = lowered.find(phrase)

    if first_pos is None:
        for term in query_terms:
            pos = lowered.find(term)
            if pos != -1:
                first_pos = pos
                break

    if first_pos is None:
        snippet = text[:260]
    else:
        start = max(0, first_pos - radius)
        end = min(len(text), first_pos + radius)
        snippet = text[start:end]

    snippet = re.sub(r"\s+", " ", snippet).strip()

    if first_pos and first_pos > 0:
        snippet = "..." + snippet
    if first_pos is not None and first_pos + radius < len(text):
        snippet = snippet + "..."

    return snippet[:320]
