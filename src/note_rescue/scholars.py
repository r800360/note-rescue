from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .paths import CONFIG_DIR, VAULT_DIR
from .search import search_notes

SCHOLARS_LOCAL_PATH = CONFIG_DIR / "scholars.local.json"
SCHOLARS_LEGACY_PATH = CONFIG_DIR / "scholars.json"
SCHOLARS_EXAMPLE_PATH = CONFIG_DIR / "scholars.example.json"

NOTE_FIELDS_ACADEMIC = [
    "Notes 3.30.26",
    "2026 Winter Deep Dive",
    "2025 End of Year Deep Dive",
    "Winter 2025 Notes",
    "Fall/Winter 2025 Deep Dive",
    "Follow-up notes",
    "Notes - FA23 Grades",
    "GPA notes",
    "Grad School Plans",
    "Overall standing",
]

NOTE_FIELDS_PROFESSIONAL = [
    "Notes",
    "Professional Development Support",
    "Grad School Status",
    "Conference Attendance/ Presentations",
    "Lab / Research Interests",
    "Placements (internship/programs)",
    "Summer Placements",
    "Faculty Pairing",
    "Research?",
    "Internship/ Lab by 3rd year",
]


@dataclass
class ScholarConfig:
    id: str
    display_name: str
    full_name: str
    aliases: list[str]


@dataclass
class ScholarProfile:
    config: ScholarConfig
    academic: dict[str, str] = field(default_factory=dict)
    professional: dict[str, str] = field(default_factory=dict)
    vault_hits: list[dict[str, Any]] = field(default_factory=list)


def get_scholars_config_path() -> Path:
    if SCHOLARS_LOCAL_PATH.exists():
        return SCHOLARS_LOCAL_PATH
    if SCHOLARS_LEGACY_PATH.exists():
        return SCHOLARS_LEGACY_PATH
    raise FileNotFoundError(
        "Private scholar config not found. Copy config/scholars.example.json to "
        "config/scholars.local.json, add your scholar list and CSV paths, and "
        "keep that file out of git (already in .gitignore)."
    )


def load_scholars_config() -> dict[str, Any]:
    path = get_scholars_config_path()

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_scholar_configs() -> list[ScholarConfig]:
    data = load_scholars_config()
    scholars = []
    for item in data.get("scholars", []):
        scholars.append(
            ScholarConfig(
                id=item["id"],
                display_name=item["display_name"],
                full_name=item["full_name"],
                aliases=item.get("aliases", []),
            )
        )
    return scholars


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def resolve_scholar(query: str) -> ScholarConfig | None:
    q = normalize(query)
    if not q:
        return None

    best: ScholarConfig | None = None
    best_score = 0

    for scholar in list_scholar_configs():
        candidates = [scholar.display_name, scholar.full_name, scholar.id.replace("-", " ")]
        candidates.extend(scholar.aliases)

        for candidate in candidates:
            c = normalize(candidate)
            if not c:
                continue
            if q == c or q in c or c in q:
                score = len(c) if q == c else len(c) // 2
                if score > best_score:
                    best = scholar
                    best_score = score

    return best


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []

    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def row_matches_scholar(row: dict[str, str], scholar: ScholarConfig, name_keys: list[str]) -> bool:
    row_name = ""
    for key in name_keys:
        if row.get(key):
            row_name = row[key]
            break

    if not row_name:
        return False

    rn = normalize(row_name)
    targets = [normalize(scholar.full_name), normalize(scholar.display_name)]
    targets.extend(normalize(a) for a in scholar.aliases)

    for target in targets:
        if target and (target in rn or rn in target):
            return True

    return False


def clean(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.strip())


def pick_notes(fields: list[str], data: dict[str, str], limit: int = 4) -> list[str]:
    notes = []
    for key in fields:
        text = clean(data.get(key, ""))
        if text and text not in notes:
            notes.append(text)
        if len(notes) >= limit:
            break
    return notes


def load_scholar_profile(query: str, include_vault: bool = True, vault_limit: int = 8) -> ScholarProfile | None:
    scholar = resolve_scholar(query)
    if not scholar:
        return None

    cfg = load_scholars_config()
    academic_rows = read_csv_rows(Path(cfg["academic_csv"]))
    professional_rows = read_csv_rows(Path(cfg["professional_csv"]))

    academic = {}
    professional = {}

    for row in academic_rows:
        if row_matches_scholar(row, scholar, ["Name"]):
            academic = {k: clean(v) for k, v in row.items() if clean(v)}
            break

    for row in professional_rows:
        if row_matches_scholar(row, scholar, ["Scholar Name", "Name"]):
            professional = {k: clean(v) for k, v in row.items() if clean(v)}
            break

    profile = ScholarProfile(config=scholar, academic=academic, professional=professional)

    if include_vault:
        terms = set()
        for value in [scholar.display_name, scholar.full_name, *scholar.aliases]:
            for part in value.split():
                if len(part) >= 3:
                    terms.add(part)

        seen_paths: set[str] = set()
        for term in sorted(terms, key=len, reverse=True):
            for hit in search_notes(term, limit=vault_limit):
                if hit["path"] in seen_paths:
                    continue
                text_lower = Path(hit["path"]).read_text(encoding="utf-8", errors="ignore").lower()
                if any(normalize(a) in text_lower for a in [scholar.full_name, *scholar.aliases[:3]]):
                    profile.vault_hits.append(hit)
                    seen_paths.add(hit["path"])

        profile.vault_hits.sort(key=lambda h: h.get("score", 0), reverse=True)
        profile.vault_hits = profile.vault_hits[:vault_limit]

    return profile


def format_profile_text(profile: ScholarProfile, topic: str = "") -> str:
    s = profile.config
    a = profile.academic
    p = profile.professional

    lines = [
        f"{'=' * 60}",
        f"  {s.full_name} ({s.display_name})",
        f"{'=' * 60}",
        "",
    ]

    def section(title: str, items: list[tuple[str, str]]):
        shown = [(k, v) for k, v in items if v]
        if not shown:
            return
        lines.append(title)
        lines.append("-" * len(title))
        for key, value in shown:
            lines.append(f"  {key}: {value}")
        lines.append("")

    section(
        "Basics",
        [
            ("Cohort", a.get("Cohort") or p.get("Cohort", "")),
            ("Email", a.get("Emails") or p.get("Emails", "")),
            ("PID", a.get("PID") or p.get("PID", "")),
            ("Major", a.get("Major/Minor") or p.get("Major/Minor", "")),
            ("Enrollment", a.get("Enrollment") or p.get("Enrollment", "")),
            ("Graduating", a.get("Graduating") or p.get("Graduating", "")),
        ],
    )

    section(
        "Academic standing",
        [
            ("Cumulative GPA", a.get("Cumulative GPA", "")),
            ("Fall 2025", a.get("Fall 2025", "")),
            ("Winter 2026", a.get("Winter 2026", "")),
            ("Spring 2026 units", a.get("Spring 2026 units", "")),
            ("GPA notes", a.get("GPA notes", "")),
            ("Overall standing", a.get("Overall standing", "")),
        ],
    )

    section(
        "Research & professional",
        [
            ("Research interests", p.get("Lab / Research Interests") or a.get("Lab / Research Interests", "")),
            ("Faculty pairing", p.get("Faculty Pairing") or a.get("Mentorship/Student Orgs", "")),
            ("Placements", p.get("Placements (internship/programs)", "")),
            ("Summer plans", p.get("Summer Placements") or a.get("Summer Placements", "")),
            ("Research active", p.get("Research?", "")),
            ("Conferences", p.get("Conference Attendance/ Presentations", "")),
            ("Grad school", p.get("Grad School Status") or a.get("Grad School Plans", "")),
        ],
    )

    advisor_notes = pick_notes(NOTE_FIELDS_ACADEMIC, a, limit=3)
    prof_notes = pick_notes(NOTE_FIELDS_PROFESSIONAL, p, limit=2)
    all_notes = advisor_notes + [n for n in prof_notes if n not in advisor_notes]

    if all_notes:
        lines.append("Recent mentor notes")
        lines.append("-------------------")
        for note in all_notes:
            lines.append(f"  - {note[:500]}{'...' if len(note) > 500 else ''}")
        lines.append("")

    if topic:
        lines.append(f"Vault search: {topic}")
        lines.append("-------------------")
        for hit in search_notes(f"{s.display_name} {topic}", limit=5):
            lines.append(f"  * {hit['rel_path']}")
            lines.append(f"    {hit['snippet'][:200]}")
        lines.append("")

    if profile.vault_hits:
        lines.append("Related notes in your vault")
        lines.append("---------------------------")
        for hit in profile.vault_hits[:5]:
            lines.append(f"  * {hit['rel_path']}")
            lines.append(f"    {hit['snippet'][:200]}")
        lines.append("")

    return "\n".join(lines)


def build_handoff_paragraph(profile: ScholarProfile) -> str:
    s = profile.config
    a = profile.academic
    p = profile.professional

    cohort = a.get("Cohort") or p.get("Cohort", "")
    major = a.get("Major/Minor") or p.get("Major/Minor", "")
    email = a.get("Emails") or p.get("Emails", "")
    gpa = a.get("Cumulative GPA", "")
    recent_gpa = a.get("Winter 2026") or a.get("Fall 2025", "")
    standing = a.get("Overall standing", "")

    research = p.get("Lab / Research Interests") or a.get("Lab / Research Interests", "")
    faculty = p.get("Faculty Pairing") or a.get("Mentorship/Student Orgs", "")
    placements = p.get("Placements (internship/programs)", "")
    summer = p.get("Summer Placements") or a.get("Summer Placements", "")
    grad = p.get("Grad School Status") or a.get("Grad School Plans", "")
    conferences = p.get("Conference Attendance/ Presentations", "")

    notes = pick_notes(NOTE_FIELDS_ACADEMIC, a, limit=2)
    if not notes:
        notes = pick_notes(NOTE_FIELDS_PROFESSIONAL, p, limit=2)

    parts = [
        f"{s.full_name} ({cohort}, {major}) is enrolled in PATHS for the 2025-26 academic year."
    ]

    if gpa:
        gpa_bit = f"Cumulative GPA is {gpa}"
        if recent_gpa:
            gpa_bit += f" (most recent term around {recent_gpa})"
        parts.append(gpa_bit + ".")

    if standing:
        parts.append(f"Overall standing: {standing}.")

    if research:
        parts.append(f"Research/professional interests: {research}.")

    if faculty:
        parts.append(f"Faculty/lab pairing: {faculty}.")

    if placements:
        parts.append(f"Current placements: {placements}.")

    if summer:
        parts.append(f"Summer plans: {summer}.")

    if conferences:
        parts.append(f"Conference activity: {conferences}.")

    if grad:
        parts.append(f"Graduate school trajectory: {grad}.")

    if notes:
        parts.append(f"Recent mentor context: {' '.join(notes)}")

    parts.append(
        f"Recommended handoff focus: continue academic and research momentum, "
        f"support internship/grad-school planning, and maintain regular check-ins on progress and wellbeing."
    )

    if email:
        parts.append(f"Contact: {email}.")

    return " ".join(parts)
