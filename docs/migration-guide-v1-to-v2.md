# Migration Guide: Command Schema v1 to v2

This guide explains how to migrate MQTT command publishers from the legacy schema v1 format to the schema v2 format used by `mqtt_command_receiver.yaml`.

Schema v2 is the preferred contract because it is explicit, safer to validate, and aligns directly with native Home Assistant service calls.

## Why migrate

Compared with v1, schema v2 provides:

- a stable top-level envelope
- explicit `service`, `target`, and `data` fields
- clearer validation against allowed domains and allowed areas
- easier support for additional writable Home Assistant domains
- a command model that more closely matches Home Assistant service execution

## Compatibility mode

During migration, set the receiver blueprint input:

- `Command Schema Mode` = `v1_v2_compat`

This allows legacy v1 payloads to continue working while you update publishers.

After all publishers have been updated and validated, switch to:

- `Command Schema Mode` = `v2_only`

## Schema comparison

| Area | v1 | v2 |
|---|---|---|
| Top-level structure | Entity-id keyed object | Explicit envelope with `schema`, `service`, `target`, `data` |
| Dispatch model | Blueprint interprets entity-specific shape | Blueprint dispatches native Home Assistant service calls |
| Validation | Looser compatibility path | Stronger validation on service domain, target shape, and area/domain allowlists |
| Extensibility | Harder to scale consistently | Easier to extend to more domains and command shapes |
| Recommended status | Deprecated | Preferred |

## v2 field contract

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

### Required fields

| Field | Required | Type | Notes |
|---|---|---|---|
| `schema` | Yes | string | Must be `v2`. |
| `service` | Yes | string | Must be `domain.service`. |
| `target` | Yes | object | Home Assistant target object. |
| `data` | Yes | object | Home Assistant service data object. Can be empty `{}`. |

### Accepted target forms

- `target.entity_id`: string or array of strings
- `target.area_id`: string or array of strings

## Migration steps

1. Keep the receiver in `v1_v2_compat` mode.
2. Inventory every publisher that writes to your command topic.
3. Replace v1 entity-keyed payloads with v2 envelopes.
4. Verify `Allowed Domains` covers every writable domain you need.
5. Verify area allowlists if using `target.area_id` or entity targets across multiple areas.
6. Test commands in Home Assistant and confirm the expected service is dispatched.
7. Remove remaining v1 publishers.
8. Switch the receiver to `v2_only`.

## Mapping examples

### Light power on

v1:

```json
{
  "light.desk_light": {
    "power": "on"
  }
}
```

v2:

```json
{
  "schema": "v2",
  "service": "light.turn_on",
  "target": {
    "entity_id": ["light.desk_light"]
  },
  "data": {}
}
```

### Light power off

v1:

```json
{
  "light.desk_light": {
    "power": "off"
  }
}
```

v2:

```json
{
  "schema": "v2",
  "service": "light.turn_off",
  "target": {
    "entity_id": ["light.desk_light"]
  },
  "data": {}
}
```

### Light brightness

v2:

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

### Switch on

v1:

```json
{
  "switch.kitchen_fan": {
    "switch": "on"
  }
}
```

v2:

```json
{
  "schema": "v2",
  "service": "switch.turn_on",
  "target": {
    "entity_id": ["switch.kitchen_fan"]
  },
  "data": {}
}
```

### Switch off

v2:

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

### Climate mode and temperature

v1:

```json
{
  "climate.bedroom_ac": {
    "mode": "cool",
    "temperature": 24
  }
}
```

v2 usually becomes one or more native service calls depending on your publisher workflow.

Set HVAC mode:

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

Set temperature:

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

### Cover open

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

### Cover set position

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

### Fan turn on with percentage

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

### Lock lock

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

### Lock unlock

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

### Area-targeted command

```json
{
  "schema": "v2",
  "service": "light.turn_off",
  "target": {
    "area_id": ["living_room"]
  },
  "data": {}
}
```

## Validation behavior in v2

Schema v2 commands are validated before dispatch:

- `service` must be `domain.service`
- `target` must be a JSON object
- `data` must be a JSON object
- service domain must pass `Allowed Domains`
- target entity domains must match the service domain
- target scope must pass area allowlist checks

If validation fails, the blueprint writes warning logs and does not dispatch the command.

## Migration checklist

- [ ] Every publisher now emits `schema: v2`.
- [ ] Every command uses `service`, `target`, and `data`.
- [ ] No external publisher still sends v1 entity-keyed payloads.
- [ ] `Allowed Domains` includes every required writable domain.
- [ ] Area allowlist configuration matches intended target scope.
- [ ] Receiver can be switched to `v2_only` without breaking active clients.

## Recommended rollout strategy

1. Enable `v1_v2_compat`.
2. Upgrade one publisher at a time.
3. Test by domain: `light`, `switch`, `climate`, `cover`, `fan`, `lock`.
4. Monitor warning logs for remaining legacy traffic.
5. Switch to `v2_only` after a clean transition window.

## Related documentation

- `README.md` for overview, support matrix, and payload examples
- `mqtt_command_receiver.yaml` for actual receiver contract and blueprint inputs
- `CHANGELOG.md` for release history and deprecation notes
