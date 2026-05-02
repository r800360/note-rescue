from pathlib import Path
from typing import List, Dict

from .paths import VAULT_DIR


def search_notes(query: str, limit: int = 20) -> List[Dict]:
    """
    Simple full-text search over the Markdown vault.
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
        score = sum(lowered.count(term) for term in query_terms)

        if score > 0:
            snippet = make_snippet(text, query_terms)
            results.append({
                "path": str(path),
                "score": score,
                "snippet": snippet,
            })

    results.sort(key=lambda x: x["score"], reverse=True)
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