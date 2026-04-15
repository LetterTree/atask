from datetime import datetime, timezone

PROJECT_FILE = ".project.atask"
VALID_STATES = {"todo", "doing", "blocked", "done", "cancelled"}


def new_project(title: str) -> dict:
    return {"ver": 1, "title": title, "tasks": []}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
