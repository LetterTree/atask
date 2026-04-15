from datetime import datetime, timezone
from atask.errors import NotFoundError, ConflictError, ValidationError
from atask.schema import now_iso, VALID_STATES


def find_task_by_key(project: dict, key: str) -> dict | None:
    for t in project["tasks"]:
        if t["key"] == key:
            return t
    return None


def _find_node_recursive(nodes: list, id: str) -> dict | None:
    for node in nodes:
        if node["id"] == id:
            return node
        found = _find_node_recursive(node.get("tasks", []), id)
        if found:
            return found
    return None


def find_node_by_id(project: dict, task_key: str, id: str) -> dict | None:
    task = find_task_by_key(project, task_key)
    if not task:
        return None
    return _find_node_recursive(task.get("tasks", []), id)


def _all_ids_in_task(task: dict) -> set:
    ids = set()
    def collect(nodes):
        for n in nodes:
            ids.add(n["id"])
            collect(n.get("tasks", []))
    collect(task.get("tasks", []))
    return ids


def add_main_task(project: dict, key: str, title: str, desc: str) -> dict:
    if find_task_by_key(project, key):
        raise ConflictError(f"Main task key '{key}' already exists")
    project["tasks"].append({
        "key": key,
        "title": title,
        "desc": desc,
        "st": "todo",
        "ct": now_iso(),
        "dt": None,
        "tasks": [],
    })
    return project


def add_subtask(project: dict, task_key: str, id: str, title: str, desc: str, parent_id: str = None) -> dict:
    task = find_task_by_key(project, task_key)
    if not task:
        raise NotFoundError(f"Main task '{task_key}' not found")

    existing_ids = _all_ids_in_task(task)
    if id in existing_ids:
        raise ConflictError(f"Subtask id '{id}' already exists in task '{task_key}'")

    new_node = {
        "id": id,
        "title": title,
        "desc": desc,
        "st": "todo",
        "ct": now_iso(),
        "dt": None,
        "tasks": [],
    }

    if parent_id is None:
        parent = task
    else:
        parent = _find_node_recursive(task.get("tasks", []), parent_id)
        if not parent:
            raise NotFoundError(f"Parent node '{parent_id}' not found in task '{task_key}'")

    if parent.get("st") in ("done", "cancelled"):
        raise ValidationError(f"Cannot add subtask to a '{parent['st']}' node")

    parent["tasks"].append(new_node)
    return project


def _find_and_update_node(nodes: list, id: str, new_status: str, dt: str | None) -> bool:
    for node in nodes:
        if node["id"] == id:
            node["st"] = new_status
            if new_status == "done":
                node["dt"] = dt
            return True
        if _find_and_update_node(node.get("tasks", []), id, new_status, dt):
            return True
    return False


def set_task_status(project: dict, task_key: str, id: str | None, new_status: str) -> dict:
    now = now_iso()
    if id is None:
        task = find_task_by_key(project, task_key)
        if not task:
            raise NotFoundError(f"Main task '{task_key}' not found")
        task["st"] = new_status
        if new_status == "done":
            task["dt"] = now
        return project

    task = find_task_by_key(project, task_key)
    if not task:
        raise NotFoundError(f"Main task '{task_key}' not found")
    found = _find_and_update_node(task.get("tasks", []), id, new_status, now)
    if not found:
        raise NotFoundError(f"Subtask '{id}' not found in task '{task_key}'")
    return project


def find_prunable_tasks(project: dict, now: object) -> list:
    from atask.validators import is_prunable
    prunable = []
    for task in project["tasks"]:
        if is_prunable(task, now):
            prunable.append(("__main__", task["key"]))
        else:
            for node in _collect_all_nodes(task.get("tasks", [])):
                if is_prunable(node, now):
                    prunable.append((task["key"], node["id"]))
    return prunable


def _collect_all_nodes(nodes: list) -> list:
    result = []
    for n in nodes:
        result.append(n)
        result.extend(_collect_all_nodes(n.get("tasks", [])))
    return result


def prune_tasks(project: dict, prunable: list) -> dict:
    main_keys = {key for (scope, key) in prunable if scope == "__main__"}
    node_ids = {key for (scope, key) in prunable if scope != "__main__"}

    project["tasks"] = [t for t in project["tasks"] if t["key"] not in main_keys]
    for task in project["tasks"]:
        task["tasks"] = _prune_nodes(task.get("tasks", []), node_ids)
    return project


def _prune_nodes(nodes: list, ids: set) -> list:
    result = []
    for n in nodes:
        if n["id"] not in ids:
            n["tasks"] = _prune_nodes(n.get("tasks", []), ids)
            result.append(n)
    return result
