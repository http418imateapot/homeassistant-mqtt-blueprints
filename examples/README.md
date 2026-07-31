# Experiments and Examples

These labs exercise the behavior implemented by the two Home Assistant blueprints and teach
the repository's pytest suite. Every lab has matching numbered Python steps and a clean Jupyter
Notebook. The shell and batch launchers run all steps and print a final summary.

Full goals, expected output, and troubleshooting are in the
[Experiment Guide](../docs/experiments.md).

## Prerequisites

- Python 3.10 or newer.
- Mosquitto or another MQTT 3.1.1/5 broker for labs 01-04.
- Optional Home Assistant test instance with both blueprints enabled for end-to-end behavior.
- VS Code Jupyter support or `nbconvert` for notebooks.

Install only the experiment dependencies from the repository root. Create the virtual
environment, activate it, then install:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r examples/requirements.txt
```

On Windows, activate with `.venv\Scripts\activate` (cmd) or `.venv\Scripts\Activate.ps1`
(PowerShell) instead of `source`.

## Lab Index

| Lab | Scripts | Notebook | Subject |
|---|---|---|---|
| 01 | [telemetry scripts](scripts/lab01_telemetry_subscribe/) | [telemetry notebook](notebooks/lab01_telemetry_subscribe.ipynb) | Subscribe to and validate event/heartbeat telemetry |
| 02 | [command scripts](scripts/lab02_command_v2/) | [command notebook](notebooks/lab02_command_v2.ipynb) | Build and publish six schema v2 commands |
| 03 | [rejection scripts](scripts/lab03_allowlist_reject/) | [rejection notebook](notebooks/lab03_allowlist_reject.ipynb) | Exercise allowlist, domain mismatch, and v1 rejection paths |
| 04 | [metadata scripts](scripts/lab04_retained_metadata/) | [metadata notebook](notebooks/lab04_retained_metadata.ipynb) | Read retained Discovery and capability metadata |
| 05 | [pytest scripts](scripts/lab05_unit_testing/) | [pytest notebook](notebooks/lab05_unit_testing.ipynb) | Learn Arrange/Act/Assert, parameterization, selection, and failures |

## Run a Lab

One-click bash and Windows examples:

```bash
bash examples/scripts/lab01_telemetry_subscribe/run_all.sh --seconds 15
```

```bat
examples\scripts\lab01_telemetry_subscribe\run_all.bat --seconds 15
```

Run one numbered step from the repository root:

```bash
python -m examples.scripts.lab01_telemetry_subscribe.step_01_connect
python -m examples.scripts.lab01_telemetry_subscribe.step_02_subscribe_validate --seconds 15
```

The shell launchers pick the first working interpreter out of `python3` and `python`
(a non-functional Windows Store alias is skipped); set the `PYTHON` environment variable
to force a specific interpreter, e.g. the one inside your activated virtual environment.

Broker defaults are `127.0.0.1:1883`. All MQTT steps accept `--host`, `--port`,
`--username`, and `--password`. The equivalent environment variables are `MQTT_HOST`,
`MQTT_PORT`, `MQTT_USERNAME`, and `MQTT_PASSWORD`. A connection failure prints setup guidance
without an unhandled traceback; scripts return a nonzero exit code and notebooks continue.

Execute a notebook from top to bottom in VS Code, or validate a clean copy from the command line:

```bash
python -m jupyter nbconvert --to notebook --execute \
  examples/notebooks/lab05_unit_testing.ipynb --output-dir=.notebook-output
```