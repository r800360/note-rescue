import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

from .paths import CATEGORIES_PATH


def load_categories() -> Dict[str, List[str]]:
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def classify_text(text: str) -> Tuple[str, Dict[str, int]]:
    """
    Simple keyword-based classifier.

    Returns:
      best_category, score_by_category
    """
    categories = load_categories()
    lowered = text.lower()

    scores = {}

    for category, keywords in categories.items():
        score = 0
        for keyword in keywords:
            pattern = re.escape(keyword.lower())
            matches = re.findall(pattern, lowered)
            score += len(matches)
        scores[category] = score

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "Inbox", scores

    return best_category, scores


def make_safe_filename(text: str, fallback: str = "untitled") -> str:
    """
    Creates a readable filename from the note content.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if not lines:
        title = fallback
    else:
        title = lines[0]

    title = title[:80]
    title = title.lower()
    title = re.sub(r"[^a-z0-9]+", "-", title)
    title = title.strip("-")

    if not title:
        title = fallback

    return title