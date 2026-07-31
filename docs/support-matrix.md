# Support Matrix

Compatibility and capability details for `mqtt_telemetry_uploader.yaml` and
`mqtt_command_receiver.yaml`.

Related documents: [MQTT Contract Reference](mqtt-contract.md) | [Testing Guide](testing.md) | [Migration Guide](migration-guide-v1-to-v2.md)

## Home Assistant

| Area | Support Status | Notes |
|---|---|---|
| Home Assistant blueprint import | Supported | Blueprints are designed for import through public raw GitHub URLs. |
| Home Assistant automation blueprint domain | Required | Both blueprints require `blueprint.domain: automation`. |
| Command receiver service dispatch | Supported | Uses native Home Assistant service calls with `service`, `target`, and `data`. |
| Area-based allowlist enforcement | Supported | Area validation is applied in schema v2 command flow. |

## MQTT Broker Compatibility

| Broker Capability | Status | Notes |
|---|---|---|
| MQTT 3.1.1 style topic publish/subscribe | Supported | Standard publish/subscribe usage only. |
| Retained messages | Required for full feature set | Used for telemetry availability, discovery config, and capability metadata topics. |
| Username/password authentication | Supported | Recommended for production brokers. |
| TLS | Recommended | Strongly recommended for production or remote access scenarios. |
| Broker-specific extensions | Not required | Project is intended to remain vendor-neutral. |

This project is expected to work with any broker that correctly supports standard MQTT
publish/subscribe behavior and retained messages. If a broker has unusual retained-message
behavior, discovery and capability metadata may not behave as expected.

## Tested Domain Capability Scope

| Domain | Telemetry Uploader | Command Receiver | Discovery | Notes |
|---|---|---|---|---|
| `sensor` | Supported | No | Supported | Read-only telemetry domain. |
| `binary_sensor` | Supported | No | Supported | Read-only telemetry domain. |
| `light` | Supported | Supported | Supported | Writable via schema v2 service calls. |
| `switch` | Supported | Supported | Supported | Writable via schema v2 service calls. |
| `climate` | Supported | Supported | Supported | Supports `hvac_mode` and `temperature` telemetry records. |
| `cover` | Supported | Supported | Supported | `position` telemetry emitted when `current_position` is available. |
| `fan` | Supported | Supported | Supported | `percentage` telemetry emitted when available. |
| `lock` | Supported | Supported | Supported | Telemetry is state-based. |

Current discovery implementation maps:

- `binary_sensor` entities -> Discovery component `binary_sensor`
- `sensor`, `switch`, `light`, `climate`, `cover`, `fan`, `lock` entities -> Discovery component `sensor`

Because all non-`binary_sensor` domains map to the read-only `sensor` component, entities
created through discovery are state mirrors; control still goes through the command topic.
Support for additional discovery mappings may be added over time.
