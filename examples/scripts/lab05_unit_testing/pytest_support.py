from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]


def run_pytest(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        "-m",
        "pytest",
        *arguments,
        "--basetemp=.pytest-tmp",
    ]
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def show_output(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())