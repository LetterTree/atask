import json
from pathlib import Path

from atask.schema import PROJECT_FILE


def project_file_path(cwd: Path = None) -> Path:
    return (cwd or Path.cwd()) / PROJECT_FILE


def load(cwd: Path = None) -> dict:
    path = project_file_path(cwd)
    return json.loads(path.read_text(encoding="utf-8"))


def save(data: dict, cwd: Path = None) -> None:
    path = project_file_path(cwd)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def exists(cwd: Path = None) -> bool:
    return project_file_path(cwd).exists()


def create(data: dict, cwd: Path = None) -> None:
    path = project_file_path(cwd)
    if path.exists():
        raise FileExistsError(f"{PROJECT_FILE} already exists")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
