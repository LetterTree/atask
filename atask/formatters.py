def _format_node(node: dict, indent: int) -> list[str]:
    prefix = "  " * indent
    lines = [f"{prefix}[{node['st']}] {node['id']} {node['title']}"]
    for child in node.get("tasks", []):
        lines.extend(_format_node(child, indent + 1))
    return lines


def format_tree(project: dict) -> str:
    if not project.get("tasks"):
        return "(no tasks)"
    lines = []
    for task in project["tasks"]:
        lines.append(f"[{task['st']}] {task['key']} {task['title']}")
        for child in task.get("tasks", []):
            lines.extend(_format_node(child, 1))
    return "\n".join(lines)
