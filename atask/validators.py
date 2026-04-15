from datetime import datetime, timezone, timedelta
from atask.errors import ValidationError
from atask.schema import VALID_STATES

VALID_TRANSITIONS: dict[str, set] = {
    "todo": {"doing", "cancelled"},
    "doing": {"done", "blocked", "cancelled"},
    "blocked": {"doing"},
    "done": set(),
    "cancelled": set(),
}


def validate_transition(current: str, target: str) -> None:
    allowed = VALID_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise ValidationError(
            f"Invalid transition '{current}' -> '{target}'. "
            f"Allowed from '{current}': {sorted(allowed) or 'none'}"
        )


def is_finished_state(state: str) -> bool:
    return state in {"done", "cancelled"}


def can_mark_done(task_or_node: dict) -> bool:
    for child in task_or_node.get("tasks", []):
        if not is_finished_state(child["st"]):
            return False
        if not can_mark_done(child):
            return False
    return True


def is_prunable(task: dict, now: datetime) -> bool:
    if task.get("st") != "done":
        return False
    dt_str = task.get("dt")
    if not dt_str:
        return False
    try:
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (now - dt) > timedelta(days=14)
    except ValueError:
        return False


def validate_project(project: dict) -> list[str]:
    errors = []

    seen_keys = set()
    for task in project.get("tasks", []):
        key = task.get("key")
        if not key:
            errors.append("Main task missing 'key'")
        elif key in seen_keys:
            errors.append(f"Duplicate main task key: '{key}'")
        else:
            seen_keys.add(key)

        st = task.get("st")
        if st not in VALID_STATES:
            errors.append(f"Task '{key}': invalid state '{st}'")

        if st == "done" and task.get("tasks"):
            child_errors = _check_parent_done_constraint(key, task)
            errors.extend(child_errors)

        seen_ids: set = set()
        errors.extend(_validate_nodes(task.get("tasks", []), key, seen_ids))

    return errors


def _check_parent_done_constraint(label: str, node: dict) -> list[str]:
    errors = []
    for child in node.get("tasks", []):
        if child["st"] not in ("done", "cancelled"):
            errors.append(
                f"Node '{label}' is done but child '{child.get('id', '?')}' is '{child['st']}'"
            )
        errors.extend(_check_parent_done_constraint(child.get("id", "?"), child))
    return errors


def _validate_nodes(nodes: list, task_key: str, seen_ids: set) -> list[str]:
    errors = []
    for node in nodes:
        id_ = node.get("id")
        if not id_:
            errors.append(f"Task '{task_key}': subtask missing 'id'")
        elif id_ in seen_ids:
            errors.append(f"Task '{task_key}': duplicate subtask id '{id_}'")
        else:
            seen_ids.add(id_)

        st = node.get("st")
        if st not in VALID_STATES:
            errors.append(f"Task '{task_key}' / '{id_}': invalid state '{st}'")

        if st == "done":
            errors.extend(_check_parent_done_constraint(id_, node))

        errors.extend(_validate_nodes(node.get("tasks", []), task_key, seen_ids))
    return errors
