# MQTT Contract Reference

This document is the full MQTT topic and payload contract implemented by
`mqtt_telemetry_uploader.yaml` and `mqtt_command_receiver.yaml`.

Related documents: [Testing Guide](testing.md) | [Release Process](release.md) | [ADR Index](adr/README.md)

## MQTT Topic Conventions

### Telemetry Publish Topic

`{mqtt_base_topic}/telemetry/{domain}`

- `mqtt_base_topic`: Blueprint input, default `homeassistant`.
- `domain`: Home Assistant entity domain, such as `sensor`, `switch`, `light`, `climate`, `binary_sensor`, `cover`, `fan`, or `lock`.
- Published with QoS 1, not retained.

### Telemetry Availability Topic (Retained)

`{mqtt_base_topic}/telemetry/availability`

- Published as retained `online` by the uploader automation at the end of every run.
- Used by Discovery config as `availability_topic`.

### Command Subscribe Topic

`{mqtt_command_topic}`

- `mqtt_command_topic`: Blueprint input, default `homeassistant/commands`.
- For consistency, set this to `{mqtt_base_topic}/commands` when using capability metadata `write_contract.command_topic`, because the uploader always advertises `{mqtt_base_topic}/commands` as the command topic.

### Discovery Config Topics (Retained)

`{mqtt_discovery_prefix}/{component}/mqtt_bridge/{domain}_{object_id}/config`

- `mqtt_discovery_prefix`: Blueprint input, default `homeassistant`.
- `component`: `binary_sensor` for `binary_sensor` entities; `sensor` for all other supported domains (`sensor`, `light`, `switch`, `climate`, `cover`, `fan`, `lock`).
- Published with QoS 1, retained, and only during heartbeat-triggered runs.

### Capability Metadata Topics (Retained)

`{mqtt_base_topic}/telemetry/capabilities/{entity_id_with_slash}`

- Example: `homeassistant/telemetry/capabilities/light/desk_lamp`
- Published with QoS 1, retained, and only during heartbeat-triggered runs.

### QoS and Retain Summary

| Topic | QoS | Retained |
|---|---|---|
| `{mqtt_base_topic}/telemetry/{domain}` | 1 | No |
| `{mqtt_base_topic}/telemetry/availability` | 1 | Yes |
| `{mqtt_discovery_prefix}/{component}/mqtt_bridge/{domain}_{object_id}/config` | 1 | Yes |
| `{mqtt_base_topic}/telemetry/capabilities/{entity_id_with_slash}` | 1 | Yes |

## Telemetry Payload (Publisher)

Top-level fields:

| Field | Type | Description |
|---|---|---|
| `timestamp` | string (UTC ISO8601) | Publish timestamp. |
| `area` | string or null | Home Assistant area name of this grouped payload. |
| `trigger_reason` | string | Trigger source, `state_changed` or `heartbeat`. |
| `sample_type` | string | `event` for state-triggered publish, `heartbeat` for timer publish. |
| `telemetries` | array | Entity telemetry records. |

Telemetry record fields:

| Field | Type | Description |
|---|---|---|
| `name` | string | Metric name (`state`, `hvac_mode`, `temperature`, `position`, `percentage`). |
| `value` | string, number, or null | Metric value. |
| `entity` | string | Entity id, for example `light.desk_lamp`. |
| `friendly_name` | string | Display label only. Not identity or authorization key. |
| `domain` | string | Entity domain. |
| `unit` | string or null | Unit for `sensor` state, `climate` temperature, `cover` position (`%`), and `fan` percentage (`%`). `null` otherwise. |

`sample_type` indicates whether a message is a real state event or a periodic heartbeat snapshot.

- `event`: emitted when Home Assistant triggers a real state change.
- `heartbeat`: emitted when the automation republishes the current snapshot on a timer.

Downstream consumers should treat `sample_type=heartbeat` as a snapshot sync signal, not as a control event.

Record fields per telemetry item are strict and fixed: `name`, `value`, `entity`, `friendly_name`, `domain`, `unit`.

`area` is represented in payload metadata and can be `null` when an entity has no assigned Home Assistant area.

Entities are grouped by `(area, domain)`. On a state-changed run, only the group containing the changed entity is published; on a heartbeat run, all groups are published.

### Sensor Example

Sensor states that parse as numbers are published as numbers; `unavailable`, `unknown`, and missing states become `null`.

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

### Light / Switch / Binary Sensor / Lock Example

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

`light`, `switch`, `binary_sensor`, and `lock` use the same single `state` record shape, with `unit` set to `null`.

Heartbeat messages use the same payload shape, but set `sample_type` to `heartbeat` and `trigger_reason` to `heartbeat`.

### Climate

Emits an `hvac_mode` record (when the state is valid) and a `temperature` record (when the `temperature` attribute exists).

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

### Cover

```json
{
  "timestamp": "2026-06-20T12:34:56.789000Z",
  "area": "living_room",
  "trigger_reason": "state_changed",
  "sample_type": "event",
  "telemetries": [
    {
      "name": "state",
      "value": "open",
      "entity": "cover.living_room_blind",
      "friendly_name": "Living Room Blind",
      "domain": "cover",
      "unit": null
    },
    {
      "name": "position",
      "value": 80,
      "entity": "cover.living_room_blind",
      "friendly_name": "Living Room Blind",
      "domain": "cover",
      "unit": "%"
    }
  ]
}
```

`position` is only included when the cover entity exposes a `current_position` attribute.

### Fan

```json
{
  "timestamp": "2026-06-20T12:34:56.789000Z",
  "area": "bedroom",
  "trigger_reason": "state_changed",
  "sample_type": "event",
  "telemetries": [
    {
      "name": "state",
      "value": "on",
      "entity": "fan.bedroom_fan",
      "friendly_name": "Bedroom Fan",
      "domain": "fan",
      "unit": null
    },
    {
      "name": "percentage",
      "value": 50,
      "entity": "fan.bedroom_fan",
      "friendly_name": "Bedroom Fan",
      "domain": "fan",
      "unit": "%"
    }
  ]
}
```

`percentage` is only included when the fan entity exposes a `percentage` attribute.

### Lock

```json
{
  "timestamp": "2026-06-20T12:34:56.789000Z",
  "area": "entrance",
  "trigger_reason": "state_changed",
  "sample_type": "event",
  "telemetries": [
    {
      "name": "state",
      "value": "locked",
      "entity": "lock.front_door",
      "friendly_name": "Front Door",
      "domain": "lock",
      "unit": null
    }
  ]
}
```

## Command Payload v2 (Subscriber, Preferred)

```json
{
  "schema": "v2",
  "service": "light.turn_on",
  "target": {
    "entity_id": ["light.desk_light"]
  },
  "data": {
    "brightness_pct": 60
  }
}
```

Field contract:

| Field | Required | Type | Rules |
|---|---|---|---|
| `schema` | Yes | string | Must be `v2`. Payloads without a `schema` field are treated as v1. |
| `service` | Yes | string | Must be `domain.service`, for example `climate.set_temperature`. |
| `target` | Yes | object | Home Assistant service target object. |
| `data` | Yes | object | Home Assistant service data object. Can be empty `{}`. |

Contract notes:

- `service` must be `domain.service`.
- `target` and `data` must be JSON objects.
- Domain allowlist is validated against the `service` domain.
- `target.entity_id` domains must match the `service` domain.
- Target scope must pass area whitelist checks (`All Areas` and `Allowed Areas`).
- If `All Areas` is disabled but `Allowed Areas` is empty, the area filter is effectively bypassed.
- `friendly_name` is display metadata only and never used for identity or authorization.

Accepted target forms:

- `target.entity_id`: string or array of strings
- `target.area_id`: string or array of strings

If `target.entity_id` is provided, area checks are evaluated against each entity's actual area
(entities without an assigned area fail the check when `Allowed Areas` filtering is active).
If only `target.area_id` is provided, all listed area ids must be within the allowed area scope,
and at least one entity in the listed areas must match the `service` domain.

## Receiver Execution Flow

1. Receiver subscribes to `mqtt_command_topic`.
2. Parses JSON and reads `schema` (missing `schema` defaults to `v1`).
3. For `schema=v2`, validates service format, allowed domain, target domain consistency, and allowed area scope.
4. On pass, executes the Home Assistant service directly using:
   - `service: <service>`
   - `target: <target>`
   - `data: <data>`
5. On failure, writes a warning log and does not dispatch. No acknowledgement or result topic is published.

## Command Examples (Schema v2)

Light turn on:

```json
{
  "schema": "v2",
  "service": "light.turn_on",
  "target": {
    "entity_id": ["light.desk_light"]
  },
  "data": {
    "brightness_pct": 70
  }
}
```

Switch turn off:

```json
{
  "schema": "v2",
  "service": "switch.turn_off",
  "target": {
    "entity_id": ["switch.kitchen_fan"]
  },
  "data": {}
}
```

Climate set HVAC mode:

```json
{
  "schema": "v2",
  "service": "climate.set_hvac_mode",
  "target": {
    "entity_id": ["climate.bedroom_ac"]
  },
  "data": {
    "hvac_mode": "cool"
  }
}
```

Climate set temperature:

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

Cover open:

```json
{
  "schema": "v2",
  "service": "cover.open_cover",
  "target": {
    "entity_id": ["cover.living_room_blind"]
  },
  "data": {}
}
```

Cover set position:

```json
{
  "schema": "v2",
  "service": "cover.set_cover_position",
  "target": {
    "entity_id": ["cover.living_room_blind"]
  },
  "data": {
    "position": 50
  }
}
```

Fan turn on with speed:

```json
{
  "schema": "v2",
  "service": "fan.turn_on",
  "target": {
    "entity_id": ["fan.bedroom_fan"]
  },
  "data": {
    "percentage": 60
  }
}
```

Lock lock:

```json
{
  "schema": "v2",
  "service": "lock.lock",
  "target": {
    "entity_id": ["lock.front_door"]
  },
  "data": {}
}
```

Lock unlock:

```json
{
  "schema": "v2",
  "service": "lock.unlock",
  "target": {
    "entity_id": ["lock.front_door"]
  },
  "data": {}
}
```

Publish the JSON payload to the receiver topic (default `homeassistant/commands`).

## Capability Payload (Retained)

Topic format:

`{mqtt_base_topic}/telemetry/capabilities/{entity_id_with_slash}`

Example topic:

`homeassistant/telemetry/capabilities/light/desk_lamp`

Payload fields:

| Field | Type | Description |
|---|---|---|
| `entity` | string | Home Assistant entity id. |
| `domain` | string | Entity domain. |
| `area` | string or null | Area name of entity. |
| `read_contract` | object | How to read state from the telemetry stream. |
| `write_contract` | object | How to issue control commands for this entity. |

`read_contract` fields:

| Field | Type | Description |
|---|---|---|
| `state_topic` | string | Domain telemetry topic used by this entity. |
| `metric` | string | Metric selector used by discovery/capability (`state`, or `hvac_mode` for climate). |
| `payload_schema.sample_type` | array | Supported sample types: `event`, `heartbeat`. |
| `payload_schema.fields` | array | Expected top-level telemetry fields. |

`write_contract` fields:

| Field | Type | Description |
|---|---|---|
| `schema` | string or null | `v2` for writable domains; `null` for read-only domains. |
| `command_topic` | string or null | Topic to publish commands to (`{mqtt_base_topic}/commands`). |
| `envelope` | array | Required command envelope field names (`service`, `target`, `data`). |
| `service_domain` | string or null | Expected service domain for this entity. |
| `target_fields` | array | Supported target keys (`entity_id`, `area_id`). |

Writable domains: `switch`, `light`, `climate`, `cover`, `fan`, `lock`.

Read-only domains: `sensor`, `binary_sensor` (their `write_contract` has `schema: null`, `command_topic: null`, and empty `envelope`/`target_fields`).

## Discovery Payload (Retained)

The uploader publishes a retained MQTT Discovery config per selected entity, only during heartbeat-triggered runs.

Component mapping:

- `binary_sensor` entities -> Discovery component `binary_sensor`
- `sensor`, `switch`, `light`, `climate`, `cover`, `fan`, `lock` entities -> Discovery component `sensor`

Discovery payload keys:

- `name`
- `unique_id` (`mqtt_bridge_{entity_id_with_underscore}`)
- `state_topic`
- `availability_topic`
- `payload_available` / `payload_not_available` (`online` / `offline`)
- `value_template` (selects this entity's metric value from the `telemetries` array)
- `json_attributes_topic` (points to the entity's capability topic)
- `unit_of_measurement` (only for `sensor` entities with a valid unit)
- `device`
- `origin`
- `object_id` (`{domain}_{object_id}`)

## Command Payload v1 (Deprecated Compatibility)

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

v1 is accepted only when `Command Schema Mode` is `v1_v2_compat` and logs explicit deprecation warnings.
Any JSON object payload whose `schema` field is missing or not `v2` is handled as v1.

v1 behavior per domain (each entity is checked against the area and domain allowlists before dispatch):

| Domain | Accepted keys | Dispatched services |
|---|---|---|
| `switch` | `switch` or `power`: `on`/`off` | `switch.turn_on` / `switch.turn_off` |
| `light` | `switch` or `power`: `on`/`off` | `light.turn_on` / `light.turn_off` |
| `cover` | `switch` or `power`: `on`/`off` | `cover.open_cover` / `cover.close_cover` |
| `fan` | `switch` or `power`: `on`/`off` | `fan.turn_on` / `fan.turn_off` |
| `lock` | `switch` or `power`: `on`/`off` | `lock.lock` / `lock.unlock` |
| `climate` | `mode` or `hvac_mode`; `temperature` | `climate.set_hvac_mode`; `climate.set_temperature` |

When `Command Schema Mode` is `v2_only`, v1 payloads are rejected with a warning log.
