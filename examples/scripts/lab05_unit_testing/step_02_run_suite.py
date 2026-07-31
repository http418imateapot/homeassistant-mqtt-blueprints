from examples.scripts.lab_common import LabError, actual, announce, run_cli
from examples.scripts.lab05_unit_testing.pytest_support import run_pytest, show_output


def run() -> bool:
    announce(
        "02",
        "Run the unit test suite",
        "Execute every test discovered under tests/.",
        "Run python -m pytest tests -q.",
        "All validator and blueprint contract tests pass; the summary reports passed test count and duration.",
    )
    result = run_pytest(["tests", "-q"])
    show_output(result)
    if result.returncode != 0:
        raise LabError(f"pytest suite exited with code {result.returncode}")
    actual("The complete unit test suite passed.")
    return True


def main() -> int:
    return run_cli(run)


if __name__ == "__main__":
    raise SystemExit(main())