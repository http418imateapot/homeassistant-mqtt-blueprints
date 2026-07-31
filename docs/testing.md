# Testing Guide

This document covers manual end-to-end testing with `mosquitto_pub` / `mosquitto_sub`,
expected payloads, and troubleshooting for common setup mistakes.

Related documents: [MQTT Contract Reference](mqtt-contract.md) | [Release Process](release.md)

## Local Repository Validation (same as CI)

Install dependencies:

```bash
pip install -r requirements.txt
```

Run lint + structure validation:

```bash
yamllint -c .yamllint mqtt_telemetry_uploader.yaml mqtt_command_receiver.yaml .github/release.yml .github/workflows/blueprint-ci.yml .github/workflows/release.yml
python ./tools/check_blueprints.py
```

The CI workflow (`.github/workflows/blueprint-ci.yml`) validates:

1. YAML lint for blueprint and release config files.
2. Required blueprint keys (`name`, `description`, `domain`, `source_url`, `input`).
3. Basic structure checks (`trigger`, `action`, `domain: automation`, and raw GitHub `source_url`).
4. `blueprint.input` is a mapping and each input defines both `selector` and `default`.
5. Home Assistant custom YAML tags (for example `!input`) are accepted by the checker.

`tools/check_blueprints.py` uses a Home Assistant-friendly YAML loader, so files containing
tags like `!input mqtt_base_topic` are parsed correctly instead of failing with
`yaml.constructor.ConstructorError`.

## Unit Tests

Install the experiment and test dependencies, then run the pytest suite:

```bash
python -m pip install -r examples/requirements.txt
python -m pytest tests -q --basetemp=.pytest-tmp
```

Run one parameterized test case:

```bash
python -m pytest "tests/test_blueprint_contracts.py::test_blueprints_use_parallel_mode[uploader]" -q --basetemp=.pytest-tmp
```

The tests cover valid and invalid samples for `tools/check_blueprints.py`, required input defaults,
parallel execution mode, and trigger contracts in both blueprint YAML files. The guided script and
Notebook workflow is in [Lab 05](experiments.md#lab-05-unit-testing).

## Test Payloads and mosquitto_pub Examples

Set your broker parameters first:

```bash
BROKER_HOST="127.0.0.1"
BROKER_PORT="1883"
MQTT_USER="your_user"
MQTT_PASS="your_password"
```

### 1) Test Command Receiver (schema v2)

Sample command payload (v2):

```json
{
  "schema": "v2",
  "service": "climate.set_temperature",
  "target": {
    "entity_id": ["climate.bedroom_ac"]
  },
  "data": {
    "temperature": 24
  }
}
```

Publish the command:

```bash
mosquitto_pub -h "$BROKER_HOST" -p "$BROKER_PORT" -u "$MQTT_USER" -P "$MQTT_PASS" \
  -t "homeassistant/commands" \
  -m '{"schema":"v2","service":"climate.set_temperature","target":{"entity_id":["climate.bedroom_ac"]},"data":{"temperature":24}}'
```

Legacy v1 example (deprecated):

```json
{
  "switch.kitchen_fan": {
    "switch": "on"
  },
  "light.desk_light": {
    "power": "off"
  },
  "climate.bedroom_ac": {
    "mode": "cool",
    "temperature": 24
  }
}
```

### 2) Observe Telemetry Topics

Subscribe to all telemetry topics:

```bash
mosquitto_sub -h "$BROKER_HOST" -p "$BROKER_PORT" -u "$MQTT_USER" -P "$MQTT_PASS" \
  -t "homeassistant/telemetry/#" -v
```

PowerShell (Windows) examples:

```powershell
$BrokerHost = "127.0.0.1"
$BrokerPort = "1883"
$MqttUser = "your_user"
$MqttPass = "your_password"

mosquitto_pub -h $BrokerHost -p $BrokerPort -u $MqttUser -P $MqttPass -t "homeassistant/commands" -m '{"switch.kitchen_fan":{"switch":"on"},"light.desk_light":{"power":"off"},"climate.bedroom_ac":{"mode":"cool","temperature":24}}'

mosquitto_pub -h $BrokerHost -p $BrokerPort -u $MqttUser -P $MqttPass -t "homeassistant/commands" -m '{"schema":"v2","service":"light.turn_on","target":{"entity_id":["light.desk_light"]},"data":{"brightness_pct":60}}'

mosquitto_sub -h $BrokerHost -p $BrokerPort -u $MqttUser -P $MqttPass -t "homeassistant/telemetry/#" -v
```

Expected event payload example:

```json
{
  "timestamp": "2026-06-20T12:34:56.789000Z",
  "area": "living_room",
  "trigger_reason": "state_changed",
  "sample_type": "event",
  "telemetries": [
    {
      "name": "state",
      "value": "on",
      "entity": "light.desk_lamp",
      "friendly_name": "Desk Lamp",
      "domain": "light",
      "unit": null
    }
  ]
}
```

Expected heartbeat payload example:

```json
{
  "timestamp": "2026-06-20T12:34:56.789000Z",
  "area": "living_room",
  "trigger_reason": "heartbeat",
  "sample_type": "heartbeat",
  "telemetries": [
    {
      "name": "state",
      "value": "on",
      "entity": "light.desk_lamp",
      "friendly_name": "Desk Lamp",
      "domain": "light",
      "unit": null
    }
  ]
}
```

If an entity has no assigned Home Assistant area, payload `area` can be `null`.

Subscriber handling guidance:

1. Treat `sample_type=event` as event-driven updates.
2. Treat `sample_type=heartbeat` as snapshot synchronization only.
3. Do not treat heartbeat samples as control actions.

### 3) Trigger Telemetry by Changing Entity State

After enabling the uploader automation:

1. Toggle a selected `light`, `switch`, or `lock` in Home Assistant UI.
2. Open or close a selected `cover`.
3. Turn on or off a selected `fan`.
4. Change a selected `climate` mode/temperature.
5. Wait for heartbeat updates for the selected domain if no immediate state trigger applies.

If everything is configured correctly, messages should appear under:

`homeassistant/telemetry/{domain}`

## Troubleshooting

### Commands are ignored (topic mismatch)

The command receiver only listens on its `MQTT Command Topic` input (default
`homeassistant/commands`). The uploader's capability metadata always advertises
`{mqtt_base_topic}/commands` in `write_contract.command_topic`. If you change
`mqtt_base_topic` on the uploader but keep the receiver's default topic (or vice versa),
external clients following the capability metadata will publish to a topic nobody subscribes to.
Keep `MQTT Command Topic` set to `{mqtt_base_topic}/commands`.

### Commands rejected for entities without an area

When `All Areas` is disabled and `Allowed Areas` is non-empty, area checks resolve each target
entity's actual area id. An entity with no assigned area resolves to an empty area id, which is
never in the allowlist, so the command is rejected. Assign the entity to an area in Home Assistant,
or enable `All Areas`. Note: if `Allowed Areas` is left empty, the area filter is bypassed even
when `All Areas` is disabled.

### v1 payload rejected

When `Command Schema Mode` is `v2_only`, any JSON object payload without `"schema": "v2"` is
rejected with a warning log (payloads missing the `schema` field are treated as v1). Switch to
`v1_v2_compat` during migration, or send schema v2 payloads.

### Blueprint import fails

Home Assistant blueprint import requires a publicly reachable raw URL. Private repositories
or private gists usually cannot be fetched. Use the raw GitHub URLs of this public repository
(see the import badges in the [README](../README.md)).

### No dispatch and no error

Rejections and skips are written to the Home Assistant system log (`system_log.write`) at
warning or debug level. Check Settings -> System -> Logs, and enable `Verbose Debug Logs`
on the receiver for more detail. The receiver never publishes an acknowledgement or result
topic, so MQTT-side silence after a command is expected behavior.
