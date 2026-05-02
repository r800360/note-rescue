from __future__ import annotations

from .paths import PROJECT_ROOT, VAULT_DIR, DATA_DIR, CATEGORIES_PATH, get_notepadpp_backup_dir
from .state import rebuild_state_from_vault, load_state
from .status import get_notepadpp_status, get_risk_level
from .search import search_notes


def run_smoke_test() -> dict:
    results = {}

    results["project_root_exists"] = PROJECT_ROOT.exists()
    results["vault_exists"] = VAULT_DIR.exists()
    results["data_exists"] = DATA_DIR.exists()
    results["categories_exists"] = CATEGORIES_PATH.exists()
    results["notepadpp_backup_dir_exists"] = get_notepadpp_backup_dir().exists()

    rebuild = rebuild_state_from_vault()
    state = load_state()

    results["state_known_hashes"] = len(state.get("imported_hashes", {}))
    results["state_rebuilt_count"] = rebuild["rebuilt_count"]
    results["state_scanned_notes"] = rebuild["scanned_notes"]
    results["state_notes_with_hash"] = rebuild["notes_with_hash"]

    status = get_notepadpp_status()
    risk, message = get_risk_level(status["active_backup_files"])

    results["active_backup_files"] = status["active_backup_files"]
    results["vault_notes"] = status["vault_notes"]
    results["risk"] = risk
    results["risk_message"] = message

    search_results = search_notes("test", limit=3)
    results["search_runs"] = isinstance(search_results, list)

    required_true = [
        "project_root_exists",
        "vault_exists",
        "data_exists",
        "categories_exists",
        "notepadpp_backup_dir_exists",
        "search_runs",
    ]

    results["passed"] = all(results.get(k) for k in required_true)

    return results