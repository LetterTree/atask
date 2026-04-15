import json
import pytest
from conftest import run_cli, read_project_file


@pytest.fixture(autouse=True)
def init_project(project_dir):
    run_cli(["init", "--title", "test"], project_dir)
    run_cli(["add", "--task-key", "core", "--title", "Core", "--desc", "d"], project_dir)
    run_cli(["add", "--task", "core", "--id", "t1", "--title", "T1", "--desc", "d"], project_dir)


def test_validate_valid_project(project_dir):
    result = run_cli(["validate"], project_dir)
    assert result.returncode == 0, result.stdout + result.stderr


def test_validate_detects_invalid_state(project_dir):
    path = project_dir / ".project.atask"
    data = json.loads(path.read_text())
    data["tasks"][0]["tasks"][0]["st"] = "invalid_state"
    path.write_text(json.dumps(data))
    result = run_cli(["validate"], project_dir)
    assert result.returncode != 0
    assert "invalid" in result.stdout.lower() or "invalid" in result.stderr.lower()


def test_validate_detects_duplicate_task_key(project_dir):
    path = project_dir / ".project.atask"
    data = json.loads(path.read_text())
    data["tasks"].append(dict(data["tasks"][0]))
    path.write_text(json.dumps(data))
    result = run_cli(["validate"], project_dir)
    assert result.returncode != 0


def test_validate_detects_duplicate_subtask_id(project_dir):
    path = project_dir / ".project.atask"
    data = json.loads(path.read_text())
    data["tasks"][0]["tasks"].append(dict(data["tasks"][0]["tasks"][0]))
    path.write_text(json.dumps(data))
    result = run_cli(["validate"], project_dir)
    assert result.returncode != 0


def test_validate_detects_parent_done_with_unfinished_child(project_dir):
    path = project_dir / ".project.atask"
    data = json.loads(path.read_text())
    data["tasks"][0]["st"] = "done"
    # t1 is still "todo"
    path.write_text(json.dumps(data))
    result = run_cli(["validate"], project_dir)
    assert result.returncode != 0


def test_validate_reports_all_errors(project_dir):
    path = project_dir / ".project.atask"
    data = json.loads(path.read_text())
    data["tasks"][0]["tasks"][0]["st"] = "bad1"
    data["tasks"].append({"key": "core", "title": "dup", "desc": "", "st": "bad2", "ct": "", "dt": None, "tasks": []})
    path.write_text(json.dumps(data))
    result = run_cli(["validate"], project_dir)
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert combined.count("-") >= 2 or combined.count("\n") >= 2
