import argparse
import json

from examples.scripts.lab_common import actual, add_broker_arguments, announce, run_cli


DEFAULT_ENTITIES = {
    "light": "light.desk_light",
    "switch": "switch.kitchen_fan",
    "climate": "climate.bedroom_ac",
    "cover": "cover.garage_door",
    "fan": "fan.living_room",
    "lock": "lock.front_door",
}


def build_commands(entities: dict[str, str]) -> list[dict]:
    return [
        {"schema": "v2", "service": "light.turn_on", "target": {"entity_id": [entities["light"]]}, "data": {"brightness_pct": 60}},
        {"schema": "v2", "service": "switch.turn_on", "target": {"entity_id": [entities["switch"]]}, "data": {}},
        {"schema": "v2", "service": "climate.set_temperature", "target": {"entity_id": [entities["climate"]]}, "data": {"temperature": 24}},
        {"schema": "v2", "service": "cover.open_cover", "target": {"entity_id": [entities["cover"]]}, "data": {}},
        {"schema": "v2", "service": "fan.set_percentage", "target": {"entity_id": [entities["fan"]]}, "data": {"percentage": 50}},
        {"schema": "v2", "service": "lock.lock", "target": {"entity_id": [entities["lock"]]}, "data": {}},
    ]


def validate_command(command: dict) -> None:
    assert command["schema"] == "v2"
    assert isinstance(command["target"], dict)
    assert isinstance(command["data"], dict)
    service_domain, service_name = command["service"].split(".")
    assert service_domain and service_name
    assert all(
        entity_id.split(".", 1)[0] == service_domain
        for entity_id in command["target"].get("entity_id", [])
    )


def add_entity_arguments(parser: argparse.ArgumentParser) -> None:
    for domain, default in DEFAULT_ENTITIES.items():
        parser.add_argument(f"--{domain}-entity", default=default)


def entities_from_args(args: argparse.Namespace) -> dict[str, str]:
    return {domain: getattr(args, f"{domain}_entity") for domain in DEFAULT_ENTITIES}


def run(entities: dict[str, str]) -> bool:
    announce(
        "01",
        "Build and validate v2 commands",
        "Create one command example for each writable blueprint domain.",
        "Build light, switch, climate, cover, fan, and lock service/target/data envelopes.",
        "Each command uses schema v2, mapping target/data values, and matching service and entity domains.",
    )
    commands = build_commands(entities)
    for command in commands:
        validate_command(command)
        print(json.dumps(command, indent=2))
    actual(f"Built and locally validated {len(commands)} command envelopes.")
    return True


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    add_broker_arguments(result)
    add_entity_arguments(result)
    result.add_argument("--topic", default="homeassistant/commands")
    return result


def main() -> int:
    args = parser().parse_args()
    return run_cli(lambda: run(entities_from_args(args)))


if __name__ == "__main__":
    raise SystemExit(main())