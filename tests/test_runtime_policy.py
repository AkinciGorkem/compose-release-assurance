import tomllib
from pathlib import Path
from typing import Any, cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
TECHNOLOGY_STACK_PATH = PROJECT_ROOT / "docs" / "TECHNOLOGY_STACK.md"


def test_python_runtime_policy_is_consistent() -> None:
    with PYPROJECT_PATH.open("rb") as pyproject_file:
        metadata = tomllib.load(pyproject_file)

    project = cast(dict[str, Any], metadata["project"])
    assert project["requires-python"] == ">=3.14,<3.15"

    technology_stack = TECHNOLOGY_STACK_PATH.read_text(encoding="utf-8")
    assert "**Initial supported runtime:** Python 3.14" in technology_stack
