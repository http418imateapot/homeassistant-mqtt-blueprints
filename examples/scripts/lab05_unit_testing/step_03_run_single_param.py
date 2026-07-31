from examples.scripts.lab_common import LabError, actual, announce, run_cli
from examples.scripts.lab05_unit_testing.pytest_support import run_pytest, show_output


TEST_ID = "tests/test_blueprint_contracts.py::test_blueprints_use_parallel_mode[uploader]"


def run() -> bool:
    announce(
        "03",
        "Run one parameterized case",
        "Select one test case by its pytest node ID.",
        f"Run python -m pytest '{TEST_ID}' -q.",
        "Exactly one uploader case passes; the receiver parameter remains unexecuted.",
    )
    result = run_pytest([TEST_ID, "-q"])
    show_output(result)
    if result.returncode != 0:
        raise LabError(f"single pytest case exited with code {result.returncode}")
    actual("One parameterized test case passed.")
    return True


def main() -> int:
    return run_cli(run)


if __name__ == "__main__":
    raise SystemExit(main())