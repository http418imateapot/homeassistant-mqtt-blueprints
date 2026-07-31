# Release Process

Related documents: [MQTT Contract Reference](mqtt-contract.md) | [Testing Guide](testing.md)

## Version Files

This repository includes simple GitHub-friendly version files:

- `VERSION`: current project version (for example `2.3.0`).
- `CHANGELOG.md`: human-readable release history.
- `.github/release.yml`: release note category rules for GitHub Releases.

## Recommended Release Flow

1. Update `VERSION`.
2. Add a new section to `CHANGELOG.md`.
3. Commit changes and create a tag (for example `v2.3.1`).
4. Publish a GitHub Release from the tag.

The release workflow syncs the telemetry discovery `sw_version` from `VERSION` before
publishing a GitHub Release (see `.github/workflows/release.yml`).
