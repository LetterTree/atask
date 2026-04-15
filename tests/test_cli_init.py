import pytest
from conftest import run_cli, read_project_file


def test_init_creates_project_file(project_dir):
    result = run_cli(["init"], project_dir)
    assert result.returncode == 0, result.stderr
    assert (project_dir / ".project.atask").exists()


def test_init_default_title_uses_dir_name(project_dir):
    run_cli(["init"], project_dir)
    data = read_project_file(project_dir)
    assert data["title"] == project_dir.name


def test_init_custom_title(project_dir):
    result = run_cli(["init", "--title", "myproject"], project_dir)
    assert result.returncode == 0
    data = read_project_file(project_dir)
    assert data["title"] == "myproject"


def test_init_schema_structure(project_dir):
    run_cli(["init"], project_dir)
    data = read_project_file(project_dir)
    assert data["ver"] == 1
    assert isinstance(data["tasks"], list)
    assert len(data["tasks"]) == 0


def test_init_refuses_overwrite(project_dir):
    run_cli(["init"], project_dir)
    result = run_cli(["init"], project_dir)
    assert result.returncode != 0
    assert ".project.atask" in result.stderr or ".project.atask" in result.stdout
