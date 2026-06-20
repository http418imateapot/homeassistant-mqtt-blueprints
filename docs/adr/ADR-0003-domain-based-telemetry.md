# ADR-0003: Replace Category-Based Telemetry Grouping with Domain-Based Telemetries Array

- Status: Accepted
- Outcome: Solved
- Date: 2026-06-20
- Related Issue: #3

## Context
The previous telemetry uploader inferred a custom category from friendly_name, device_class, and derived metrics, then grouped multiple entities into one payload. This created several problems:

- category was project-specific and not aligned with Home Assistant standards
- group payloads could mix multiple entities, reducing traceability
- friendly_name influenced grouping logic, which is not stable for machine integration
- downstream systems could not reliably identify which entity produced each value

## Decision
Adopt a domain-based telemetry model and remove category-based grouping.

1. Topic format is changed to:
- `{mqtt_base_topic}/telemetry/{area}/{domain}`

2. Payload structure is changed from grouped telemetry object to telemetries array.

3. Each telemetry record uses a strict fixed schema:
- name
- value
- entity
- friendly_name
- domain
- unit

4. Add payload-level sample_type:
- event: state/event-driven update
- heartbeat: periodic snapshot republish

5. Retain trigger_reason for trigger provenance, but downstream event semantics should rely on sample_type.

## Implemented Result (Solved)
This decision is implemented.

- category-based routing and payload model removed
- domain-based topic routing applied
- strict telemetries array schema applied
- sample_type added to payload envelope
- README updated with schema examples and consumer guidance
- version bumped to major due to breaking format changes
- changelog updated with breaking, added, and fixed entries

## Consequences

### Positive
- aligned with Home Assistant domain semantics
- improved downstream parsing and entity-level traceability
- removed unstable friendly_name-dependent grouping logic
- reduced false interpretation risk by distinguishing event vs heartbeat

### Trade-offs
- breaking change for existing consumers using old topic/payload contracts
- consumers must migrate routing and parser logic

## Migration Notes
Consumers should update as follows:

1. Topic subscription/routing:
- from `{mqtt_base_topic}/telemetry/{location}/{category}`
- to `{mqtt_base_topic}/telemetry/{area}/{domain}`

2. Payload parsing:
- from grouped telemetry object
- to telemetries array records

3. Event interpretation:
- treat sample_type=event as event-driven updates
- treat sample_type=heartbeat as snapshot synchronization only
- do not treat heartbeat samples as control actions

## Validation
Implementation passed project checks:

- YAML lint
- blueprint structural validation

## Alternatives Considered
### Keep category-based model and only add entity field
Rejected because category remained non-standard and still coupled to unstable grouping logic.

### Move to per-entity topic only
Rejected for now because it would increase message fan-out and require wider downstream changes than needed for this ticket.

### Change command receiver format at the same time
Rejected to avoid coupling unrelated breaking changes; command receiver remains backward compatible in this scope.
