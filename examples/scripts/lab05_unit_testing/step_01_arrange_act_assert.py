from examples.scripts.lab_common import LabError, actual, announce, run_cli
from examples.scripts.lab05_unit_testing.pytest_support import run_pytest, show_output


def run() -> bool:
    announce(
        "01",
        "Find Arrange, Act, Assert",
        "Use pytest collection to identify well-named tests before running them.",
        "Collect tests/ without executing; inspect test_check_file_accepts_valid_blueprint as Arrange/Act/Assert.",
        "Pytest lists validator and blueprint contract test IDs.",
    )
    result = run_pytest(["--collect-only", "-q", "tests"])
    show_output(result)
    if result.returncode != 0:
        raise LabError(f"pytest collection exited with code {result.returncode}")
    actual("Tests collected. Fixtures/builders arrange data, check_file is the act, and assertions verify outcomes.")
    return True


def main() -> int:
    return run_cli(run)


if __name__ == "__main__":
    raise SystemExit(main())