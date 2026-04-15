import json
import subprocess
import sys
from pathlib import Path

import pytest

PYTHON = "/home/letree/.local/share/uv/python/cpython-3.11.15-linux-x86_64-gnu/bin/python3.11"


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path


def run_cli(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, "-m", "atask.cli"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def read_project_file(cwd: Path) -> dict:
    return json.loads((cwd / ".project.atask").read_text(encoding="utf-8"))
