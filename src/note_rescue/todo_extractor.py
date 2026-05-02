import re
from typing import List


TODO_PATTERNS = [
    r"^\s*-\s*\[\s*\]\s+(.+)$",
    r"^\s*TODO[:\-\s]+(.+)$",
    r"^\s*Todo[:\-\s]+(.+)$",
    r"^\s*todo[:\-\s]+(.+)$",
    r"^\s*Action item[:\-\s]+(.+)$",
    r"^\s*ACTION ITEM[:\-\s]+(.+)$",
    r"^\s*Need to[:\-\s]+(.+)$",
    r"^\s*Remember to[:\-\s]+(.+)$"
]


def extract_todos(text: str) -> List[str]:
    todos = []

    for line in text.splitlines():
        for pattern in TODO_PATTERNS:
            match = re.match(pattern, line)
            if match:
                item = match.group(1).strip()
                if item:
                    todos.append(item)

    return todos