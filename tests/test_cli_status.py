import pytest
from conftest import run_cli, read_project_file


@pytest.fixture(autouse=True)
def init_project(project_dir):
    run_cli(["init", "--title", "test"], project_dir)
    run_cli(["add", "--task-key", "core", "--title", "Core", "--desc", "d"], project_dir)
    run_cli(["add", "--task", "core", "--id", "t1", "--title", "T1", "--desc", "d"], project_dir)
    run_cli(["add", "--task", "core", "--id", "t2", "--title", "T2", "--desc", "d"], project_dir)


def test_start_todo_to_doing(project_dir):
    result = run_cli(["start", "--task", "core", "--id", "t1"], project_dir)
    assert result.returncode == 0, result.stderr
    data = read_project_file(project_dir)
    assert data["tasks"][0]["tasks"][0]["st"] == "doing"


def test_done_doing_to_done_writes_dt(project_dir):
    run_cli(["start", "--task", "core", "--id", "t1"], project_dir)
    result = run_cli(["done", "--task", "core", "--id", "t1"], project_dir)
    assert result.returncode == 0, result.stderr
    data = read_project_file(project_dir)
    node = data["tasks"][0]["tasks"][0]
    assert node["st"] == "done"
    assert node["dt"] is not None


def test_block_doing_to_blocked(project_dir):
    run_cli(["start", "--task", "core", "--id", "t1"], project_dir)
    result = run_cli(["block", "--task", "core", "--id", "t1"], project_dir)
    assert result.returncode == 0
    data = read_project_file(project_dir)
    assert data["tasks"][0]["tasks"][0]["st"] == "blocked"


def test_cancel_doing_to_cancelled(project_dir):
    run_cli(["start", "--task", "core", "--id", "t1"], project_dir)
    result = run_cli(["cancel", "--task", "core", "--id", "t1"], project_dir)
    assert result.returncode == 0
    data = read_project_file(project_dir)
    assert data["tasks"][0]["tasks"][0]["st"] == "cancelled"


def test_cancel_todo_to_cancelled(project_dir):
    result = run_cli(["cancel", "--task", "core", "--id", "t1"], project_dir)
    assert result.returncode == 0
    data = read_project_file(project_dir)
    assert data["tasks"][0]["tasks"][0]["st"] == "cancelled"


def test_blocked_to_doing(project_dir):
    run_cli(["start", "--task", "core", "--id", "t1"], project_dir)
    run_cli(["block", "--task", "core", "--id", "t1"], project_dir)
    result = run_cli(["start", "--task", "core", "--id", "t1"], project_dir)
    assert result.returncode == 0
    data = read_project_file(project_dir)
    assert data["tasks"][0]["tasks"][0]["st"] == "doing"


def test_reject_todo_to_done(project_dir):
    result = run_cli(["done", "--task", "core", "--id", "t1"], project_dir)
    assert result.returncode != 0


def test_reject_done_to_doing(project_dir):
    run_cli(["start", "--task", "core", "--id", "t1"], project_dir)
    run_cli(["done", "--task", "core", "--id", "t1"], project_dir)
    result = run_cli(["start", "--task", "core", "--id", "t1"], project_dir)
    assert result.returncode != 0


def test_reject_cancelled_to_doing(project_dir):
    run_cli(["cancel", "--task", "core", "--id", "t1"], project_dir)
    result = run_cli(["start", "--task", "core", "--id", "t1"], project_dir)
    assert result.returncode != 0


def test_parent_done_fails_with_unfinished_child(project_dir):
    # t1 is todo, core has t1 and t2 — both unfinished
    result = run_cli(["done", "--task", "core"], project_dir)
    assert result.returncode != 0


def test_parent_done_succeeds_when_all_children_finished(project_dir):
    run_cli(["start", "--task", "core", "--id", "t1"], project_dir)
    run_cli(["done", "--task", "core", "--id", "t1"], project_dir)
    run_cli(["cancel", "--task", "core", "--id", "t2"], project_dir)
    run_cli(["start", "--task", "core"], project_dir)
    result = run_cli(["done", "--task", "core"], project_dir)
    assert result.returncode == 0, result.stderr
