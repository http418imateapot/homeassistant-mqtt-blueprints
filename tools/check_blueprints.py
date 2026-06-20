#!/usr/bin/env python3
from pathlib import Path
import sys
import yaml

FILES = [
    Path("mqtt_telemetry_uploader.yaml"),
    Path("mqtt_command_receiver.yaml"),
]

REQUIRED_BLUEPRINT_KEYS = {"name", "description", "domain", "source_url", "input"}


class HomeAssistantLoader(yaml.SafeLoader):
    """Safe loader that tolerates Home Assistant custom tags like !input."""


def _construct_unknown_tag(loader: yaml.SafeLoader, node: yaml.Node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


HomeAssistantLoader.add_constructor(None, _construct_unknown_tag)

def fail(message: str) -> None:
    raise SystemExit(message)

def check_file(path: Path) -> None:
    if not path.exists():
        fail(f"{path}: file not found")

    data = yaml.load(path.read_text(encoding="utf-8"), Loader=HomeAssistantLoader)

    if not isinstance(data, dict):
        fail(f"{path}: top-level YAML must be a mapping")

    bp = data.get("blueprint")
    if not isinstance(bp, dict):
        fail(f"{path}: missing blueprint mapping")

    missing = REQUIRED_BLUEPRINT_KEYS - set(bp.keys())
    if missing:
        fail(f"{path}: missing blueprint keys: {sorted(missing)}")

    if bp.get("domain") != "automation":
        fail(f"{path}: blueprint.domain must be automation")

    source_url = bp.get("source_url", "")
    if "raw.githubusercontent.com" not in source_url:
        fail(f"{path}: source_url should be a raw GitHub URL")

    if "trigger" not in data:
        fail(f"{path}: missing trigger section")

    if "action" not in data:
        fail(f"{path}: missing action section")

    inputs = bp.get("input")
    if not isinstance(inputs, dict):
        fail(f"{path}: blueprint.input must be a mapping")

    for input_name, input_def in inputs.items():
        if not isinstance(input_def, dict):
            fail(f"{path}: input '{input_name}' must be a mapping")

        if "selector" not in input_def:
            fail(f"{path}: input '{input_name}' missing selector")

        if "default" not in input_def:
            fail(f"{path}: input '{input_name}' missing default")

def main() -> int:
    for file_path in FILES:
        check_file(file_path)

    print("Blueprint strict validation passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
