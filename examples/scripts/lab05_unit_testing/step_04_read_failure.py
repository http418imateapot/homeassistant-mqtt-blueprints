from pathlib import Path
import subprocess
import sys
import tempfile

from examples.scripts.lab_common import LabError, actual, announce, run_cli
from examples.scripts.lab05_unit_testing.pytest_support import ROOT, show_output


def run() -> bool:
    announce(
        "04",
        "Read a pytest failure",
        "Generate an isolated intentional failure and interpret pytest's assertion diff.",
        "Run a temporary test asserting an actual mode of serial against expected parallel.",
        "Pytest exits 1, shows expected/actual values and a short summary; the lab treats this expected failure as success.",
    )
    with tempfile.TemporaryDirectory(prefix="pytest-demo-", dir=ROOT) as temp_dir:
        temp_path = Path(temp_dir)
        test_path = temp_path / "test_expected_failure.py"
        test_path.write_text(
            "def test_mode_is_parallel():\n"
            "    actual_mode = 'serial'\n"
            "    assert actual_mode == 'parallel'\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_path), "-q", f"--basetemp={temp_path / 'tmp'}"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        show_output(result)
    if result.returncode != 1 or "AssertionError" not in result.stdout:
        raise LabError(f"expected pytest failure was not observed (exit code {result.returncode})")
    actual("Expected failure observed: assertion detail identifies serial as actual and parallel as expected.")
    return True


def main() -> int:
    return run_cli(run)


if __name__ == "__main__":
    raise SystemExit(main())