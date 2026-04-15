import pytest
from conftest import run_cli, read_project_file


@pytest.fixture(autouse=True)
def init_project(project_dir):
    run_cli(["init", "--title", "test"], project_dir)


def test_add_main_task(project_dir):
    result = run_cli(["add", "--task-key", "core", "--title", "Core", "--desc", "desc"], project_dir)
    assert result.returncode == 0, result.stderr
    data = read_project_file(project_dir)
    assert data["tasks"][0]["key"] == "core"
    assert data["tasks"][0]["st"] == "todo"


def test_add_subtask(project_dir):
    run_cli(["add", "--task-key", "core", "--title", "Core", "--desc", "d"], project_dir)
    result = run_cli(["add", "--task", "core", "--id", "t1", "--title", "Task 1", "--desc", "d"], project_dir)
    assert result.returncode == 0, result.stderr
    data = read_project_file(project_dir)
    assert data["tasks"][0]["tasks"][0]["id"] == "t1"


def test_add_nested_subtask(project_dir):
    run_cli(["add", "--task-key", "core", "--title", "Core", "--desc", "d"], project_dir)
    run_cli(["add", "--task", "core", "--id", "t1", "--title", "Task 1", "--desc", "d"], project_dir)
    result = run_cli(["add", "--task", "core", "--parent", "t1", "--id", "t1.1", "--title", "Sub", "--desc", "d"], project_dir)
    assert result.returncode == 0, result.stderr
    data = read_project_file(project_dir)
    assert data["tasks"][0]["tasks"][0]["tasks"][0]["id"] == "t1.1"


def test_add_duplicate_task_key(project_dir):
    run_cli(["add", "--task-key", "core", "--title", "Core", "--desc", "d"], project_dir)
    result = run_cli(["add", "--task-key", "core", "--title", "Core2", "--desc", "d"], project_dir)
    assert result.returncode != 0


def test_add_duplicate_subtask_id(project_dir):
    run_cli(["add", "--task-key", "core", "--title", "Core", "--desc", "d"], project_dir)
    run_cli(["add", "--task", "core", "--id", "t1", "--title", "T1", "--desc", "d"], project_dir)
    result = run_cli(["add", "--task", "core", "--id", "t1", "--title", "T1dup", "--desc", "d"], project_dir)
    assert result.returncode != 0


def test_add_subtask_to_done_parent_fails(project_dir):
    run_cli(["add", "--task-key", "core", "--title", "Core", "--desc", "d"], project_dir)
    run_cli(["add", "--task", "core", "--id", "t1", "--title", "T1", "--desc", "d"], project_dir)
    run_cli(["start", "--task", "core", "--id", "t1"], project_dir)
    run_cli(["done", "--task", "core", "--id", "t1"], project_dir)
    result = run_cli(["add", "--task", "core", "--parent", "t1", "--id", "t1.1", "--title", "Sub", "--desc", "d"], project_dir)
    assert result.returncode != 0


def test_add_subtask_to_cancelled_parent_fails(project_dir):
    run_cli(["add", "--task-key", "core", "--title", "Core", "--desc", "d"], project_dir)
    run_cli(["add", "--task", "core", "--id", "t1", "--title", "T1", "--desc", "d"], project_dir)
    run_cli(["cancel", "--task", "core", "--id", "t1"], project_dir)
    result = run_cli(["add", "--task", "core", "--parent", "t1", "--id", "t1.1", "--title", "Sub", "--desc", "d"], project_dir)
    assert result.returncode != 0
