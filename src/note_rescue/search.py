from __future__ import annotations

from typing import List, Dict

from .paths import VAULT_DIR


def search_notes(query: str, limit: int = 20) -> List[Dict]:
    """
    Simple full-text search over the Markdown vault.

    Ranking:
    - Notes containing all query terms rank above partial matches.
    - Then notes with higher term frequency rank higher.
    """
    query_terms = [term.lower() for term in query.split() if term.strip()]
    results = []

    if not query_terms:
        return results

    for path in VAULT_DIR.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        lowered = text.lower()
        term_counts = {term: lowered.count(term) for term in query_terms}
        matched_terms = [term for term, count in term_counts.items() if count > 0]

        if not matched_terms:
            continue

        all_terms_match = len(matched_terms) == len(query_terms)
        raw_score = sum(term_counts.values())

        score = raw_score
        if all_terms_match:
            score += 1000

        snippet = make_snippet(text, query_terms)

        results.append({
            "path": str(path),
            "score": score,
            "raw_score": raw_score,
            "matched_terms": len(matched_terms),
            "total_terms": len(query_terms),
            "all_terms_match": all_terms_match,
            "snippet": snippet,
        })

    results.sort(
        key=lambda x: (
            x["all_terms_match"],
            x["matched_terms"],
            x["raw_score"],
        ),
        reverse=True,
    )

    return results[:limit]


def make_snippet(text: str, query_terms: list[str], radius: int = 160) -> str:
    lowered = text.lower()

    first_pos = None

    for term in query_terms:
        pos = lowered.find(term)
        if pos != -1:
            first_pos = pos
            break

    if first_pos is None:
        return text[:300].replace("\n", " ")

    start = max(0, first_pos - radius)
    end = min(len(text), first_pos + radius)

    snippet = text[start:end]
    snippet = snippet.replace("\n", " ")

    if start > 0:
        snippet = "..." + snippet

    if end < len(text):
        snippet = snippet + "..."

    return snippet