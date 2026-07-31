import argparse
import json

from examples.scripts.lab_common import actual, add_broker_arguments, announce, run_cli


def scenarios() -> list[tuple[str, str, dict]]:
    return [
        (
            "domain not allowed",
            "Configure Allowed Domains to light only; switch is then rejected.",
            {"schema": "v2", "service": "switch.turn_on", "target": {"entity_id": ["switch.kitchen_fan"]}, "data": {}},
        ),
        (
            "target/service domain mismatch",
            "The light service targets a switch entity.",
            {"schema": "v2", "service": "light.turn_on", "target": {"entity_id": ["switch.kitchen_fan"]}, "data": {}},
        ),
        (
            "v1 rejected in v2_only",
            "Configure Command Schema Mode to v2_only; a mapping without schema=v2 is v1.",
            {"light.desk_light": {"power": "on"}},
        ),
    ]


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    add_broker_arguments(result)
    result.add_argument("--topic", default="homeassistant/commands")
    return result


def run() -> bool:
    announce(
        "01",
        "Build rejection scenarios",
        "Prepare commands that exercise three receiver rejection paths.",
        "Create a disallowed domain, a target-domain mismatch, and a v1 payload for v2_only mode.",
        "Each payload maps to a specific validation variable in the receiver blueprint.",
    )
    for name, setup, payload in scenarios():
        print(f"\n{name}: {setup}\n{json.dumps(payload, indent=2)}")
    actual("Prepared 3 rejection scenarios; receiver settings noted above are required.")
    return True


def main() -> int:
    parser().parse_args()
    return run_cli(run)


if __name__ == "__main__":
    raise SystemExit(main())