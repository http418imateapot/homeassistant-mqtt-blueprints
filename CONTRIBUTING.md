# Contributing

Thanks for your interest in contributing to this project.

This repository provides universal, local-first Home Assistant blueprints for bi-directional MQTT sync. The goal is to keep the blueprints easy to import, predictable to operate, and practical for real Home Assistant deployments.

## Scope and Design Goals

Contributions should align with these project goals:

- **Local-first**: avoid designs that require cloud services.
- **Vendor-neutral**: prefer generic MQTT and Home Assistant patterns over vendor-specific behavior.
- **Low-friction setup**: keep import and configuration simple for end users.
- **Stable contracts**: preserve predictable topic structures and JSON payload schemas.
- **Safe defaults**: avoid exposing sensitive payload details in logs unless explicitly enabled.

If a proposal adds significant complexity, please explain why the added maintenance cost is worth it.

## Ways to Contribute

You can help by:

- reporting bugs or regression cases
- improving documentation and examples
- proposing support for additional Home Assistant entity domains
- improving validation, CI, and release tooling
- refining topic, discovery, and payload contract consistency

## Before You Start

Before making a larger change, it is helpful to open an issue first and describe:

- the problem you are solving
- the expected user workflow
- whether the change is backward compatible
- whether it changes MQTT topics, payloads, discovery metadata, or command schema behavior

This is especially important for changes that affect interoperability.

## Repository Structure

- `mqtt_telemetry_uploader.yaml` — publishes Home Assistant telemetry to MQTT and retained discovery metadata
- `mqtt_command_receiver.yaml` — receives MQTT JSON commands and dispatches Home Assistant service calls
- `tools/check_blueprints.py` — strict validation for blueprint structure and required metadata
- `README.md` — user-facing setup and contract documentation
- `CHANGELOG.md` — notable changes
- `VERSION` — release version source used by the release workflow

## Development Guidelines

When contributing, please follow these rules:

- Keep blueprint payloads minimal, explicit, and predictable.
- Avoid hardcoded cloud endpoints, vendor APIs, or vendor-specific assumptions.
- Prefer backward-compatible changes when possible.
- Treat topic and payload changes as API changes for downstream consumers.
- Preserve safe-by-default logging behavior.
- Keep README examples consistent with actual blueprint behavior.
- Do not introduce hidden behavior that is not documented.

## Breaking Changes and Compatibility

Please be careful with:

- MQTT topic structure changes
- telemetry JSON schema changes
- command schema changes
- retained discovery/config topic behavior
- allowlist and permission model changes

If a change is breaking or migration-sensitive:

- document it clearly in `CHANGELOG.md`
- update `README.md`
- include migration notes in the pull request description
- prefer staged compatibility modes when practical

## Testing

At minimum, before opening a pull request:

1. Run the repository checks locally.
2. Import the affected blueprint(s) into a test Home Assistant instance.
3. Verify the relevant MQTT topics and payloads.
4. Confirm README examples still match actual behavior.

### Local checks

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run YAML lint and blueprint validation:

```bash
yamllint -c .yamllint mqtt_telemetry_uploader.yaml mqtt_command_receiver.yaml .github/release.yml .github/workflows/blueprint-ci.yml .github/workflows/release.yml
python -m py_compile tools/check_blueprints.py
python ./tools/check_blueprints.py
```

### Manual verification suggestions

For telemetry changes:

- test at least one entity from each affected domain
- verify publish topics
- verify payload field names and value shapes
- verify retained discovery metadata if applicable
- verify heartbeat and event-triggered behavior if relevant

For command receiver changes:

- test schema v2 behavior first
- test v1 compatibility only when the PR touches compatibility paths
- verify area/domain allowlist behavior
- verify logs do not expose full payloads unless verbose mode is enabled

## Pull Request Checklist

Before submitting a PR, please confirm:

- [ ] The change fits the project scope.
- [ ] User-facing behavior changes are documented in `README.md` if needed.
- [ ] `CHANGELOG.md` is updated for notable user-facing changes.
- [ ] `VERSION` is updated only when appropriate for release intent.
- [ ] Local validation passes.
- [ ] Migration notes are included for compatibility-impacting changes.
- [ ] The PR is focused on one logical change.

## Commit and PR Style

- Use clear, concise commit messages.
- Prefer one logical change per pull request.
- Explain the user impact, not only the implementation detail.
- Include sample payloads or topic examples when changing contracts.
- If the PR changes behavior, mention whether it is backward compatible.

## Documentation Expectations

Documentation is part of the product. If you change behavior, also update the relevant documentation:

- `README.md` for setup, examples, topics, and payload contracts
- `CHANGELOG.md` for notable released changes
- inline blueprint descriptions and input descriptions where needed

## Code of Conduct and Security

Please follow the repository `CODE_OF_CONDUCT.md`.

If you find a security issue or a dangerous control-path concern, please use the process described in `SECURITY.md` instead of opening a public issue first.
