# Copilot Instructions — homeassistant-mqtt-blueprints

## Project Overview

This repository provides two Home Assistant Automation Blueprints that bridge HA entities with a local MQTT broker:

- `mqtt_telemetry_uploader.yaml` — monitors selected HA entities and publishes grouped telemetry to MQTT.
- `mqtt_command_receiver.yaml` — listens on an MQTT topic and dispatches validated HA service calls.

**Core design principles:**
- Local-first: no cloud lock-in, no virtual helper sensors.
- Clean JSON contracts for downstream consumers (gateways, dashboards, rule engines).
- Safe-by-default logging: never print full payloads in debug logs unless explicitly enabled by the user.
- Backward-compatible changes preferred; breaking changes require a major version bump.

Current version: see `VERSION` file.

---

## Repository Structure

```
mqtt_telemetry_uploader.yaml   # Blueprint: telemetry publisher
mqtt_command_receiver.yaml     # Blueprint: command receiver
tools/check_blueprints.py      # Blueprint structure validator (used by CI)
.yamllint                      # yamllint config (line-length disabled, consistent indentation)
VERSION                        # Semver string (e.g. 2.3.0)
CHANGELOG.md                   # Keep a Changelog format
docs/adr/                      # Architecture Decision Records
.github/workflows/
  blueprint-ci.yml             # PR/push validation: yamllint + blueprint structure check
  release.yml                  # Release pipeline: syncs sw_version from VERSION
.github/ISSUE_TEMPLATE/        # Bug report + feature request templates
.github/pull_request_template.md
```

---

## Blueprint Structure Rules

Every blueprint file must conform to the following structure. `tools/check_blueprints.py` enforces these at CI time.

### Required `blueprint` keys

```yaml
blueprint:
  name: ...
  description: ...
  domain: automation          # must be exactly "automation"
  source_url: https://raw.githubusercontent.com/...  # must contain raw.githubusercontent.com
  input:
    some_input:
      selector: ...           # every input must have a selector
      default: ...            # every input must have a default
```

### Required top-level sections

```yaml
trigger: ...
action: ...
```

### YAML style

- Follow `.yamllint` rules: line-length disabled, `indent-sequences: consistent`.
- Use `!input` tags for blueprint input references inside `variables`, `trigger`, and `action`.
- HA-specific tags like `!input` are valid YAML in this project. Do not remove or quote them.

---

## Supported Domains

| Domain | Telemetry published | Writable via commands |
|---|---|---|
| `light` | ✅ | ✅ |
| `switch` | ✅ | ✅ |
| `climate` | ✅ | ✅ |
| `cover` | ✅ | ✅ |
| `fan` | ✅ | ✅ |
| `lock` | ✅ | ✅ |
| `sensor` | ✅ | ❌ |
| `binary_sensor` | ✅ | ❌ |

When adding a new domain, update **both** blueprints (telemetry + receiver), README domain tables and examples, CHANGELOG, and CI-facing README section.

---

## MQTT Topic Conventions

### Telemetry topics (uploader publishes)

| Topic | Retained | Description |
|---|---|---|
| `{base_topic}/telemetry/{domain}` | No | Telemetry payload (QoS 1) |
| `{base_topic}/telemetry/availability` | **Yes** | `"online"` |
| `{discovery_prefix}/{component}/mqtt_bridge/{domain}_{object_id}/config` | **Yes** | MQTT Discovery config |
| `{base_topic}/telemetry/capabilities/{entity_id_with_slash}` | **Yes** | Capability metadata |

### Command topic (receiver subscribes)

| Topic | Description |
|---|---|
| `{mqtt_command_topic}` | Default: `homeassistant/commands` |

---

## Telemetry Payload Schema

Top-level fields:

```json
{
  "timestamp": "<UTC ISO8601>",
  "area": "<area name or null>",
  "trigger_reason": "state_changed | heartbeat",
  "sample_type": "event | heartbeat",
  "telemetries": [ /* array of telemetry records */ ]
}
```

Telemetry record (strict, fixed fields):

```json
{
  "name": "state | hvac_mode | temperature | position | percentage",
  "value": "<string, number, or null>",
  "entity": "domain.object_id",
  "friendly_name": "<display label only, NOT used for identity or authorization>",
  "domain": "<HA domain>",
  "unit": "<unit string or null>"
}
```

**`sample_type` semantics:**
- `event`: real state-driven update. Downstream may treat as a control signal.
- `heartbeat`: periodic snapshot. Downstream must NOT treat as a control event.

**Domain-specific telemetry fields:**
- `sensor`: `state` record; value is cast to float when possible.
- `light`, `switch`, `binary_sensor`, `lock`: `state` record; `unit` is `null`.
- `climate`: `hvac_mode` record + optional `temperature` record.
- `cover`: `state` record + optional `position` record (from `current_position` attribute).
- `fan`: `state` record + optional `percentage` record.

**`friendly_name` is display metadata only.** Never use it for identity, grouping logic, or authorization checks.

---

## Command Payload Schema

### v2 (preferred)

```json
{
  "schema": "v2",
  "service": "domain.service_name",
  "target": { "entity_id": ["domain.object_id"] },
  "data": { }
}
```

Validation rules enforced by `mqtt_command_receiver.yaml`:
1. Payload must be a JSON mapping.
2. `schema` must be `"v2"`.
3. `service` must be `"domain.service"` format.
4. `service` domain must be in the configured `command_domains` allowlist.
5. `target.entity_id` domains must match the `service` domain.
6. Target entities/areas must pass the configured area whitelist.
7. `target` and `data` must both be JSON objects.

### v1 (deprecated, compat only)

```json
{
  "entity.object_id": { "switch": "on", "power": "off", "mode": "cool", "temperature": 24 }
}
```

Accepted only when `command_schema_mode` is `v1_v2_compat`. Always logs a deprecation warning. Planned for removal; see `v1_deprecation_timeline` input.

---

## Capability Payload Schema

Published retained per entity at heartbeat time:

```json
{
  "entity": "domain.object_id",
  "domain": "light",
  "area": "living_room",
  "read_contract": {
    "state_topic": "{base_topic}/telemetry/{domain}",
    "metric": "state",
    "payload_schema": {
      "sample_type": ["event", "heartbeat"],
      "fields": ["timestamp", "area", "trigger_reason", "sample_type", "telemetries"]
    }
  },
  "write_contract": {
    "schema": "v2",
    "command_topic": "{base_topic}/commands",
    "envelope": ["service", "target", "data"],
    "service_domain": "light",
    "target_fields": ["entity_id", "area_id"]
  }
}
```

Read-only domains (`sensor`, `binary_sensor`) have `write_contract.schema = null` and empty envelope.

---

## Logging Rules

- **Always** use `system_log.write` (not `logger.log`) for all log entries.
- Log levels: `debug` for normal flow steps, `warning` for rejected/deprecated commands.
- Default behavior: debug logs must **not** print full payload content.
- `verbose_debug_logs` input (command receiver only): when `true`, print command field names only — never full payload values.
- Log prefix: always start with `[MQTT_Bridge]` for easy log filtering.

---

## Security Rules

- MQTT broker access should be local/VPN-only in production.
- Never commit secrets, tokens, or runtime credential files.
- `friendly_name` must never be used for authorization or identity checks.
- Command receiver must validate service domain, target domain consistency, and area scope before any dispatch.
- All schema v2 validation checks must pass atomically — no partial dispatch.

---

## Versioning and Changelog

- `VERSION` contains a semver string (e.g. `2.3.0`).
- `CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com/) with sections: `Added`, `Changed`, `Fixed`, `Deprecated`.
- Breaking payload or topic changes → major version bump.
- New domain or feature additions → minor version bump.
- Bug fixes → patch version bump.
- `sw_version` inside Discovery payloads in `mqtt_telemetry_uploader.yaml` must match `VERSION`. The release pipeline syncs this automatically.

Release flow:
1. Update `VERSION`.
2. Add a new section to `CHANGELOG.md`.
3. Commit and create a git tag (e.g. `v2.3.0`).
4. Publish a GitHub Release from the tag.

---

## CI Validation

Run locally before opening a PR (same steps as CI):

```bash
pip install -r requirements.txt

yamllint -c .yamllint mqtt_telemetry_uploader.yaml mqtt_command_receiver.yaml \
  .github/release.yml .github/workflows/blueprint-ci.yml .github/workflows/release.yml

python -m py_compile tools/check_blueprints.py
python ./tools/check_blueprints.py
```

`tools/check_blueprints.py` uses `HomeAssistantLoader` to tolerate `!input` tags. Do not replace this loader with plain `yaml.safe_load`.

---

## Architecture Decision Records

ADRs live in `docs/adr/`. Create a new ADR when making a design decision that:
- changes topic format or payload schema,
- adds or removes a supported domain,
- introduces or removes a command schema version,
- changes grouping or publish logic.

ADR filename format: `ADR-NNNN-short-description.md`

ADR status values: `Proposed`, `Accepted`, `Rejected`, `Superseded`, `Solved`

---

## Common Copilot Tasks

### Add a new domain

1. Add `{domain}_entities` input to `mqtt_telemetry_uploader.yaml` (with `selector` and `default: []`).
2. Add a `platform: state` trigger for the new domain in the uploader.
3. Add the domain to `_all_entities` merge in `variables`.
4. Add telemetry extraction logic in the `_telemetries_json` block (follow existing domain patterns).
5. Add Discovery component mapping in `_discovery_component` template (usually `sensor`).
6. Add the domain to `command_domains` options in `mqtt_command_receiver.yaml`.
7. Add v1 dispatch handling in the legacy compat block if the domain is writable.
8. Update README domain table, payload examples, and command examples.
9. Update CHANGELOG and bump version appropriately.

### Modify telemetry payload fields

- The `telemetries` array record schema is **strict and fixed**: `name`, `value`, `entity`, `friendly_name`, `domain`, `unit`. Do not add extra fields to records without an ADR.
- Top-level envelope fields (`timestamp`, `area`, `trigger_reason`, `sample_type`, `telemetries`) are also fixed. Changes here are breaking.

### Modify command validation logic

- All validation variables (`_v2_allowed`, `_service_valid`, etc.) are computed once per trigger in a single `variables` block before dispatch.
- Do not add conditional validation splits — keep the logic flat and readable.
- Any new validation rule must be added to both the pass path and the rejection warning log.

### Update Discovery payloads

- Discovery is published **only on heartbeat triggers** to avoid excessive retained writes.
- `unique_id` format: `mqtt_bridge_{entity_id_with_underscores}`.
- `object_id` format: `{domain}_{object_id}`.
- `device.identifiers`: always `['mqtt_bridge_homeassistant']`.
- `sw_version` in `origin` must match `VERSION`.
