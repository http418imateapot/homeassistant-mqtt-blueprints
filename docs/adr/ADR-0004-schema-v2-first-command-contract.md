# ADR-0004: Adopt Schema v2 as the Primary Command Contract

- Status: Accepted
- Outcome: Solved
- Date: 2026-06-25
- Related: #4

## Context

The project originally supported a legacy MQTT command format where the payload was keyed by Home Assistant entity id. That format was useful for early experimentation, but it became increasingly difficult to validate and extend consistently as the project evolved.

The repository needed a command contract that:

- maps cleanly to native Home Assistant service execution
- supports area and domain allowlist validation
- can scale to additional writable domains without special-case payload shapes
- is explicit enough for downstream integrations to generate reliably
- is easier to document, migrate, and validate safely

The legacy schema v1 format also made it harder to express a general command envelope because the meaning of the payload depended on entity-specific nested fields.

## Decision

Adopt schema v2 as the primary command contract for `mqtt_command_receiver.yaml`.

Schema v2 uses an explicit envelope with:

- `schema`
- `service`
- `target`
- `data`

The receiver validates the command envelope and dispatches native Home Assistant service calls directly.

Schema v1 remains available only as a temporary compatibility path through `Command Schema Mode = v1_v2_compat` during migration.

## Consequences

### Positive

- Commands now align directly with Home Assistant service semantics.
- Validation is clearer and safer because the receiver can check service domain, target structure, and area/domain allowlists explicitly.
- Extending support to additional writable domains is easier because the envelope stays stable.
- Downstream tools can generate commands more predictably.
- Documentation and examples are easier to standardize.

### Negative

- Existing publishers using v1 must migrate.
- Some v1 workflows that bundled multiple implicit actions may need to become one or more explicit v2 service calls.
- Migration guidance and compatibility messaging must be maintained until v1 is removed.

## Alternatives Considered

### Keep schema v1 as the long-term primary contract

Rejected because it is harder to validate safely, less explicit, and less scalable as more writable domains and target patterns are added.

### Introduce per-domain custom command schemas

Rejected because it would increase fragmentation, documentation burden, and implementation complexity.

### Use a custom abstraction unrelated to Home Assistant service calls

Rejected because it would create unnecessary translation logic and would move the project away from Home Assistant-native behavior.

## Migration Notes

To reduce breakage, the project introduced a compatibility mode:

- `v1_v2_compat` allows legacy v1 publishers to continue working temporarily
- `v2_only` is the intended steady-state mode

Migration guidance is documented in:

- `README.md`
- `docs/migration-guide-v1-to-v2.md`

## Validation

Schema v2 validation includes:

- service must use `domain.service` format
- `target` must be a JSON object
- `data` must be a JSON object
- service domain must pass `Allowed Domains`
- target entity domains must match the service domain
- target scope must pass allowed area checks

Commands that fail validation are not dispatched.
