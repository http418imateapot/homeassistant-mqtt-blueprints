from pathlib import Path

import pytest

from tools.check_blueprints import check_file


def write_blueprint(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "blueprint.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def valid_blueprint() -> str:
    return """\
blueprint:
  name: Test Blueprint
  description: Test fixture
  domain: automation
  source_url: https://raw.githubusercontent.com/example/repo/main/blueprint.yaml
  input:
    test_input:
      default: []
      selector:
        text:
trigger: []
action: []
"""


def test_check_file_accepts_valid_blueprint(tmp_path: Path) -> None:
    path = write_blueprint(tmp_path, valid_blueprint())

    check_file(path)


@pytest.mark.parametrize(
    ("content", "expected_message"),
    [
        ("- not-a-mapping\n", "top-level YAML must be a mapping"),
        (valid_blueprint().replace("  domain: automation\n", ""), "missing blueprint keys"),
        (valid_blueprint().replace("  domain: automation", "  domain: script"), "blueprint.domain must be automation"),
        (valid_blueprint().replace("trigger: []\n", ""), "missing trigger section"),
        (valid_blueprint().replace("action: []\n", ""), "missing action section"),
        (valid_blueprint().replace("      selector:\n        text:\n", ""), "missing selector"),
        (valid_blueprint().replace("      default: []\n", ""), "missing default"),
    ],
)
def test_check_file_rejects_invalid_blueprints(
    tmp_path: Path, content: str, expected_message: str
) -> None:
    path = write_blueprint(tmp_path, content)

    with pytest.raises(SystemExit, match=expected_message):
        check_file(path)


def test_check_file_reports_missing_file(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="file not found"):
        check_file(tmp_path / "missing.yaml")