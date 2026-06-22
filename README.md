# Universal Local-First MQTT Blueprints for Home Assistant

[![Blueprint CI](https://github.com/http418imateapot/homeassistant-mqtt-blueprints/actions/workflows/blueprint-ci.yml/badge.svg)](https://github.com/http418imateapot/homeassistant-mqtt-blueprints/actions/workflows/blueprint-ci.yml)
[![Release Pipeline](https://github.com/http418imateapot/homeassistant-mqtt-blueprints/actions/workflows/release.yml/badge.svg)](https://github.com/http418imateapot/homeassistant-mqtt-blueprints/actions/workflows/release.yml)
[![Latest Release](https://img.shields.io/github/v/release/http418imateapot/homeassistant-mqtt-blueprints?label=Release)](https://github.com/http418imateapot/homeassistant-mqtt-blueprints/releases)

A plug-and-play blueprint set for bridging Home Assistant entities with a local MQTT broker.

- Local-first design: no cloud lock-in and no virtual helper sensors required.
- Standard topic structure for telemetry and commands.
- Clean JSON payloads for easy integration with gateways, dashboards, and rule engines.

## Blueprints

1. mqtt_telemetry_uploader.yaml
2. mqtt_command_receiver.yaml

## Architecture

```mermaid
flowchart LR
  A[Home Assistant Entities] --> B[Telemetry Uploader Blueprint]
  B --> C[(MQTT Broker)]
  D[External App or Rule Engine] --> C
  C --> E[Command Receiver Blueprint]
  E --> F[Home Assistant Services]
```

## Current Design Snapshot

This is the current design baseline for open-source release:

- Telemetry uploader groups selected entities by area and domain internally, then publishes strict per-domain JSON payloads.
- Command receiver uses native MQTT trigger and dispatches commands to climate, switch, and light services.
- Command receiver includes whitelist controls by area and domain:
  - Area filter: `All Areas` + `Allowed Areas`
  - Domain filter: `Allowed Domains` (`all`, `climate`, `switch`, `light`)
- Logs are safe-by-default:
  - Debug logs do not print full payload by default.
  - Optional verbose debug mode can show command field names.
- Heartbeat interval is constrained to predefined options (`/1`, `/5`, `/10`, `/30`) to avoid invalid input.

## MQTT Topic Conventions

### Telemetry Publish Topic

`{mqtt_base_topic}/telemetry/{domain}`

- mqtt_base_topic: Blueprint input, default `homeassistant`
- domain: Home Assistant entity domain, such as `sensor`, `switch`, `light`, `climate`, or `binary_sensor`

### Command Subscribe Topic

`{mqtt_command_topic}`

- mqtt_command_topic: Blueprint input, default `homeassistant/commands`

## Payload Schemas

### Telemetry Payload (Publisher)

`sample_type` indicates whether a message is a real state event or a periodic heartbeat snapshot.

- `event`: emitted when Home Assistant triggers a real state change.
- `heartbeat`: emitted when the automation republishes the current snapshot on a timer.

Downstream consumers should treat `sample_type=heartbeat` as a snapshot sync signal, not as a control event.

Record fields per telemetry item are strict and fixed:

- `name`
- `value`
- `entity`
- `friendly_name`
- `domain`
- `unit`

`area` is represented in payload metadata and can be `null` when an entity has no assigned Home Assistant area.

#### Sensor Example

```json
{
  "timestamp": "2026-06-20T12:34:56.789000Z",
  "area": "living_room",
  "trigger_reason": "state_changed",
  "sample_type": "event",
  "telemetries": [
    {
      "name": "state",
      "value": 25.1,
      "entity": "sensor.living_room_temperature",
      "friendly_name": "Living Room Temperature",
      "domain": "sensor",
      "unit": "°C"
    }
  ]
}
```

#### Light / Switch / Binary Sensor Example

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

`light`, `switch`, and `binary_sensor` use the same single `state` record shape, with `unit` set to `null`.

Heartbeat messages use the same payload shape, but set `sample_type` to `heartbeat`.

#### Climate

```json
{
  "timestamp": "2026-06-20T12:34:56.789000Z",
  "area": "living_room",
  "trigger_reason": "state_changed",
  "sample_type": "event",
  "telemetries": [
    {
      "name": "hvac_mode",
      "value": "cool",
      "entity": "climate.bedroom_ac",
      "friendly_name": "Bedroom AC",
      "domain": "climate",
      "unit": null
    },
    {
      "name": "temperature",
      "value": 24,
      "entity": "climate.bedroom_ac",
      "friendly_name": "Bedroom AC",
      "domain": "climate",
      "unit": "°C"
    }
  ]
}
```

### Command Payload (Subscriber)

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

## Installation

### Import Prerequisites

- Recommended: host blueprints in a public GitHub repository (this project already does this).
- Alternative: use a public GitHub Gist for quick single-file testing.
- Avoid private URLs (private repo/private gist), because Home Assistant blueprint import usually cannot fetch them.

### Option A: Import via My Home Assistant

[![Open your Home Assistant instance and import Telemetry Uploader](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/http418imateapot/homeassistant-mqtt-blueprints/main/mqtt_telemetry_uploader.yaml)

[![Open your Home Assistant instance and import Command Receiver](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/http418imateapot/homeassistant-mqtt-blueprints/main/mqtt_command_receiver.yaml)

### Option B: Manual Import

1. In Home Assistant, go to Settings -> Automations & Scenes -> Blueprints.
2. Import blueprint.
3. Paste the raw GitHub URL of each YAML blueprint file.

## Quick Start

1. Import both blueprints.
2. Create one automation from `mqtt_telemetry_uploader.yaml` and select entities.
3. Create one automation from `mqtt_command_receiver.yaml` and set command topic.
4. Configure command whitelist filters:
  - `All Areas`: enabled means area filter is bypassed.
  - `Allowed Areas`: used only when `All Areas` is disabled.
  - `Allowed Domains`: supports `all`, `climate`, `switch`, `light`.
  - `Verbose Debug Logs`: optional detailed debug fields for troubleshooting.
5. Publish a JSON command payload to `homeassistant/commands`.
6. Verify telemetry messages under `homeassistant/telemetry/{domain}`.
7. Use `sample_type` on the subscriber side to distinguish event-driven updates from heartbeat snapshots.

## Test Payloads and mosquitto_pub Examples

Set your broker parameters first:

```bash
BROKER_HOST="127.0.0.1"
BROKER_PORT="1883"
MQTT_USER="your_user"
MQTT_PASS="your_password"
```

### 1) Test Command Receiver (switch/light/climate)

Sample command payload:

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

Publish the command:

```bash
mosquitto_pub -h "$BROKER_HOST" -p "$BROKER_PORT" -u "$MQTT_USER" -P "$MQTT_PASS" \
  -t "homeassistant/commands" \
  -m '{"switch.kitchen_fan":{"switch":"on"},"light.desk_light":{"power":"off"},"climate.bedroom_ac":{"mode":"cool","temperature":24}}'
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

Subscriber handling guidance:

1. Treat `sample_type=event` as event-driven updates.
2. Treat `sample_type=heartbeat` as snapshot synchronization only.
3. Do not treat heartbeat samples as control actions.

### 3) Trigger Telemetry by Changing Entity State

After enabling the uploader automation:

1. Toggle a selected `light` or `switch` in Home Assistant UI.
2. Change a selected `climate` mode/temperature.
3. Wait for heartbeat updates for the selected domain if no immediate state trigger applies.

If everything is configured correctly, messages should appear under:

`homeassistant/telemetry/{domain}`

## Security Notes

- Keep MQTT broker access local/VPN-only when possible.
- Use username/password and TLS on production brokers.
- Do not commit secrets or runtime files to this repository.

## Open-Source Operations

This repository includes collaboration and governance files:

- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `.github/ISSUE_TEMPLATE/` (bug report + feature request templates)
- `.github/pull_request_template.md`

CI is enabled via:

- `.github/workflows/blueprint-ci.yml`

Validation logic is shared via:

- `tools/check_blueprints.py`

The CI workflow validates:

1. YAML lint for blueprint and release config files.
2. Required blueprint keys (`name`, `description`, `domain`, `source_url`, `input`).
3. Basic structure checks (`trigger`, `action`, `domain: automation`, and raw GitHub `source_url`).
4. `blueprint.input` is a mapping and each input defines both `selector` and `default`.
5. Home Assistant custom YAML tags (for example `!input`) are accepted by the checker.

### Local Validation (same as CI)

Install dependencies:

```bash
pip install -r requirements.txt
```

Run lint + structure validation:

```bash
yamllint -c .yamllint mqtt_telemetry_uploader.yaml mqtt_command_receiver.yaml .github/release.yml .github/workflows/blueprint-ci.yml .github/workflows/release.yml
python ./tools/check_blueprints.py
```

`tools/check_blueprints.py` uses a Home Assistant-friendly YAML loader, so files containing tags like `!input mqtt_base_topic` are parsed correctly instead of failing with `yaml.constructor.ConstructorError`.

## Versioning

This repository includes simple GitHub-friendly version files:

- `VERSION`: current project version (for example `2.1.0`).
- `CHANGELOG.md`: human-readable release history.
- `.github/release.yml`: release note category rules for GitHub Releases.

Recommended release flow:

1. Update `VERSION`.
2. Add a new section to `CHANGELOG.md`.
3. Commit changes and create a tag (for example `v2.1.1`).
4. Publish a GitHub Release from the tag.

## License

This project uses Apache License 2.0.
