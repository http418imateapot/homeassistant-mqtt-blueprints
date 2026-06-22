# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog,
and this project follows Semantic Versioning.

## [Unreleased]
### Changed
- Updated README telemetry topic documentation to `{mqtt_base_topic}/telemetry/{domain}`.
- Clarified in README that telemetry payload `area` can be `null` when an entity has no assigned Home Assistant area.

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

