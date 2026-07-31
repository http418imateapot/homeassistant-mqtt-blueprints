from pathlib import Path

import pytest
import yaml

from tools.check_blueprints import HomeAssistantLoader


ROOT = Path(__file__).resolve().parents[1]
UPLOADER = ROOT / "mqtt_telemetry_uploader.yaml"
RECEIVER = ROOT / "mqtt_command_receiver.yaml"


def load_blueprint(path: Path) -> dict:
    return yaml.load(path.read_text(encoding="utf-8"), Loader=HomeAssistantLoader)


@pytest.mark.parametrize("path", [UPLOADER, RECEIVER], ids=["uploader", "receiver"])
def test_blueprints_use_parallel_mode(path: Path) -> None:
    blueprint = load_blueprint(path)

    assert blueprint["mode"] == "parallel"
    assert blueprint["max"] == 20


@pytest.mark.parametrize("path", [UPLOADER, RECEIVER], ids=["uploader", "receiver"])
def test_every_input_has_selector_and_default(path: Path) -> None:
    inputs = load_blueprint(path)["blueprint"]["input"]

    assert inputs
    for name, definition in inputs.items():
        assert "selector" in definition, f"{name} is missing selector"
        assert "default" in definition, f"{name} is missing default"


def test_uploader_input_defaults() -> None:
    inputs = load_blueprint(UPLOADER)["blueprint"]["input"]

    assert inputs["mqtt_base_topic"]["default"] == "homeassistant"
    assert inputs["heartbeat_minutes"]["default"] == "/1"
    assert inputs["mqtt_discovery_prefix"]["default"] == "homeassistant"
    entity_inputs = {
        "light_entities",
        "switch_entities",
        "sensor_entities",
        "binary_sensor_entities",
        "climate_entities",
        "cover_entities",
        "fan_entities",
        "lock_entities",
    }
    assert all(inputs[name]["default"] == [] for name in entity_inputs)


def test_uploader_trigger_contract() -> None:
    triggers = load_blueprint(UPLOADER)["trigger"]

    state_triggers = [trigger for trigger in triggers if trigger["platform"] == "state"]
    heartbeat_triggers = [
        trigger for trigger in triggers if trigger["platform"] == "time_pattern"
    ]
    assert len(state_triggers) == 8
    assert {trigger["id"] for trigger in state_triggers} == {"state_changed"}
    assert heartbeat_triggers == [
        {"platform": "time_pattern", "minutes": "heartbeat_minutes", "id": "heartbeat"}
    ]


def test_receiver_input_defaults_and_domains() -> None:
    inputs = load_blueprint(RECEIVER)["blueprint"]["input"]
    options = inputs["command_domains"]["selector"]["select"]["options"]

    assert inputs["mqtt_command_topic"]["default"] == "homeassistant/commands"
    assert inputs["all_command_areas"]["default"] is True
    assert inputs["command_areas"]["default"] == []
    assert inputs["command_domains"]["default"] == ["all"]
    assert inputs["verbose_debug_logs"]["default"] is False
    assert inputs["command_schema_mode"]["default"] == "v1_v2_compat"
    assert {option["value"] for option in options} == {
        "all",
        "climate",
        "cover",
        "fan",
        "light",
        "lock",
        "switch",
    }


def test_receiver_trigger_contract() -> None:
    triggers = load_blueprint(RECEIVER)["trigger"]

    assert triggers == [
        {
            "platform": "mqtt",
            "topic": "mqtt_command_topic",
            "id": "mqtt_command",
        }
    ]