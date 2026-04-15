import pytest
from conftest import run_cli, read_project_file


@pytest.fixture(autouse=True)
def init_project(project_dir):
    run_cli(["init", "--title", "test"], project_dir)


def test_tree_shows_main_task(project_dir):
    run_cli(["add", "--task-key", "core", "--title", "Core", "--desc", "d"], project_dir)
    result = run_cli(["tree"], project_dir)
    assert result.returncode == 0
    assert "core" in result.stdout
    assert "Core" in result.stdout


def test_tree_shows_status(project_dir):
    run_cli(["add", "--task-key", "core", "--title", "Core", "--desc", "d"], project_dir)
    result = run_cli(["tree"], project_dir)
    assert "[todo]" in result.stdout


def test_tree_shows_subtask_indented(project_dir):
    run_cli(["add", "--task-key", "core", "--title", "Core", "--desc", "d"], project_dir)
    run_cli(["add", "--task", "core", "--id", "t1", "--title", "T1", "--desc", "d"], project_dir)
    result = run_cli(["tree"], project_dir)
    lines = result.stdout.splitlines()
    core_line = next(l for l in lines if "core" in l)
    t1_line = next(l for l in lines if "t1" in l)
    assert lines.index(t1_line) > lines.index(core_line)
    assert t1_line.startswith("  ")


def test_tree_nested_deeper_indent(project_dir):
    run_cli(["add", "--task-key", "core", "--title", "Core", "--desc", "d"], project_dir)
    run_cli(["add", "--task", "core", "--id", "t1", "--title", "T1", "--desc", "d"], project_dir)
    run_cli(["add", "--task", "core", "--parent", "t1", "--id", "t1.1", "--title", "Sub", "--desc", "d"], project_dir)
    result = run_cli(["tree"], project_dir)
    t11_line = next(l for l in result.stdout.splitlines() if "t1.1" in l)
    assert t11_line.startswith("    ")


def test_tree_empty_project(project_dir):
    result = run_cli(["tree"], project_dir)
    assert result.returncode == 0
    assert "no tasks" in result.stdout.lower() or result.stdout.strip() == "(no tasks)"


def test_tree_no_project_file(project_dir, tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    result = run_cli(["tree"], empty)
    assert result.returncode != 0
