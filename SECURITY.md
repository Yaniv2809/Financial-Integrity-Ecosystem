# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| main    | ✅ Active           |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do not** open a public GitHub Issue for security vulnerabilities
2. Email: yaniv2809@gmail.com
3. Include a description of the vulnerability, steps to reproduce, and potential impact

I will acknowledge receipt within 48 hours and provide an update within 7 days.

## Scope

This is a test automation framework and educational project. It does not process real financial data. However, security best practices are followed:

- No secrets or API keys are committed to the repository
- Environment variables are used for sensitive configuration (`.env`)
- Docker containers run with minimal privileges
- Dependencies are monitored for known vulnerabilities
