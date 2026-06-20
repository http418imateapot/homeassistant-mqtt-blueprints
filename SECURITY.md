# Security Policy

## Reporting a Vulnerability

Please do not open a public issue for sensitive security reports.

Report vulnerabilities by opening a private security advisory on GitHub for this repository.
If that is not available, open an issue with minimal details and request a private follow-up.

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.x     | Yes       |
| < 1.0   | No        |

## Security Notes

- Restrict MQTT broker access to trusted networks or VPN.
- Use authentication and TLS in production.
- Keep command topics private and access-controlled.
