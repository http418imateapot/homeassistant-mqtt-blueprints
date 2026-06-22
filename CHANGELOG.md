# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog,
and this project follows Semantic Versioning.

## [2.1.0] - 2026-06-22
### Changed
- Telemetry publish topic was simplified to `{mqtt_base_topic}/telemetry/{domain}`.
- `area` remains in telemetry payload metadata and may be `null` when an entity has no assigned Home Assistant area.
- Updated README examples and setup guidance to match current telemetry topic and payload behavior.

### Fixed
- Fixed template key access to avoid dict-method collisions on `items`.
- Removed dependency on unsupported `combine`-based template merge path.
- Fixed grouping and repeat variable flow to avoid runtime rendering failures.
- Ensured `telemetries` is emitted as JSON array/object, not quoted JSON string.
- Normalized climate `temperature_unit` to plain string for clean JSON serialization.
- Fixed YAML indentation in repeat variables block to avoid parse errors.

## [2.0.0] - 2026-06-20
### Changed
- **Breaking:** Telemetry topic format changed from `{mqtt_base_topic}/telemetry/{location}/{category}` to `{mqtt_base_topic}/telemetry/{area}/{domain}`.
- **Breaking:** Telemetry payload schema changed from grouped `telemetry` object to strict `telemetries` array records.
- **Breaking:** Category-based payload grouping was removed. Telemetry is now published per domain.
- Telemetry records are now normalized to a strict field set: `name`, `value`, `entity`, `friendly_name`, `domain`, `unit`.
- Climate telemetry now emits domain-specific fields (`hvac_mode` and `temperature`) instead of category-derived structures.

### Added
- Added `sample_type` to telemetry payloads (`event` or `heartbeat`) for downstream event/snapshot disambiguation.
- Added Home Assistant custom YAML tag support (for example `!input`) in blueprint validation tooling.
- Added GitHub Release pipeline workflow (`.github/workflows/release.yml`).
- Added Python syntax compile check for tools in CI.

### Fixed
- Fixed blueprint checker failures caused by unknown Home Assistant YAML tags.
- Fixed README and validation docs to reflect current telemetry schema and CI/CD checks.

## [1.0.0] - 2026-06-20
### Added
- Initial open-source release of Local-First MQTT blueprints.
- Added mqtt_telemetry_uploader.yaml.
- Added mqtt_command_receiver.yaml.
- Added README with architecture, install steps, and test payload examples.
- Added Home Assistant focused .gitignore.

