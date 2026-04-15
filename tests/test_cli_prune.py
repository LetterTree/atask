import json
from datetime import datetime, timezone, timedelta
import pytest
from conftest import run_cli, read_project_file

PYTHON = "/home/letree/.local/share/uv/python/cpython-3.11.15-linux-x86_64-gnu/bin/python3.11"


def make_old_dt() -> str:
    return (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()


def make_recent_dt() -> str:
    return (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()


@pytest.fixture(autouse=True)
def init_project(project_dir):
    run_cli(["init", "--title", "test"], project_dir)
    run_cli(["add", "--task-key", "core", "--title", "Core", "--desc", "d"], project_dir)
    run_cli(["add", "--task", "core", "--id", "t1", "--title", "T1", "--desc", "d"], project_dir)
    run_cli(["add", "--task", "core", "--id", "t2", "--title", "T2", "--desc", "d"], project_dir)


def _set_done_with_dt(project_dir, task_key, subtask_id, dt_str):
    path = project_dir / ".project.atask"
    data = json.loads(path.read_text())
    for task in data["tasks"]:
        if task["key"] == task_key:
            for node in task["tasks"]:
                if node["id"] == subtask_id:
                    node["st"] = "done"
                    node["dt"] = dt_str
    path.write_text(json.dumps(data))


def test_prune_old_done_task_shown_in_dryrun(project_dir):
    _set_done_with_dt(project_dir, "core", "t1", make_old_dt())
    result = run_cli(["prune"], project_dir)
    assert result.returncode == 0
    assert "t1" in result.stdout


def test_prune_dryrun_does_not_modify_file(project_dir):
    _set_done_with_dt(project_dir, "core", "t1", make_old_dt())
    before = (project_dir / ".project.atask").read_text()
    run_cli(["prune"], project_dir)
    after = (project_dir / ".project.atask").read_text()
    assert before == after


def test_prune_apply_removes_old_done_task(project_dir):
    _set_done_with_dt(project_dir, "core", "t1", make_old_dt())
    result = run_cli(["prune", "--apply"], project_dir)
    assert result.returncode == 0
    data = read_project_file(project_dir)
    ids = [n["id"] for n in data["tasks"][0]["tasks"]]
    assert "t1" not in ids
    assert "t2" in ids


def test_prune_recent_done_not_pruned(project_dir):
    _set_done_with_dt(project_dir, "core", "t1", make_recent_dt())
    result = run_cli(["prune"], project_dir)
    assert "Nothing to prune" in result.stdout or "t1" not in result.stdout


def test_prune_todo_task_not_pruned(project_dir):
    result = run_cli(["prune"], project_dir)
    assert "Nothing to prune" in result.stdout
