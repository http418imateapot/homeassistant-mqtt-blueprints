# Contributing

Thanks for contributing to this project.

## Scope

This repository focuses on Home Assistant MQTT blueprints that are:
- Local-first
- Vendor-neutral
- Easy to import and operate

## Development Guidelines

- Keep blueprint payloads minimal and predictable.
- Avoid hardcoded cloud/vendor topics.
- Prefer backward-compatible changes when possible.
- Keep logs safe by default (do not print full payload content unless explicitly enabled).

## Pull Request Checklist

- Update blueprint description and docs when behavior changes.
- Update CHANGELOG.md for user-facing changes.
- Keep VERSION in sync with release intent.
- Ensure CI passes.

## Local Validation (same as CI)

Run these before opening a PR:

```bash
pip install -r requirements.txt
yamllint -c .yamllint mqtt_telemetry_uploader.yaml mqtt_command_receiver.yaml .github/release.yml .github/workflows/blueprint-ci.yml .github/workflows/release.yml
python ./tools/check_blueprints.py
```

Details on what CI validates are in the
[Testing Guide](docs/testing.md#local-repository-validation-same-as-ci).

## Testing

Before opening a PR:

1. Import both blueprints in a test Home Assistant instance.
2. Verify telemetry publishing and command dispatch behavior.
3. Validate MQTT topics and payload schema against the
   [MQTT Contract Reference](docs/mqtt-contract.md), using the
   [Testing Guide](docs/testing.md) payload examples.

## Commit and PR Style

- Use clear, short commit messages.
- One logical change per PR is preferred.
- Include migration notes if behavior changed.
