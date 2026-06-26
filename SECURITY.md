# Security Policy

## 1. Security Commitment

Compose Release Assurance is a publicly available, source-available, production-engineered reference implementation.

It is not certified for regulated production use. Security, integrity, and confidentiality are still treated as first-class engineering requirements.

The project must fail conservatively: an unverified mandatory check must not result in `GO`.

## 2. Supported Scope

During the pre-alpha stage, security fixes are applied to the current `main` branch.

The project currently supports local development, controlled test environments, and authorized CI runners only.

## 3. Reporting a Vulnerability

Do not open a public GitHub issue for a suspected vulnerability.

Use GitHub Private Security Advisories when the repository enables them. Until then, report the issue privately to:

```text

g.akinci@protonmail.com

```

A report should include:

* Clear description of the issue

* Affected component or file

* Reproduction steps

* Potential impact

* Proof of concept only when it does not expose secrets or private infrastructure

* Suggested mitigation, when available

Do not include passwords, tokens, internal URLs, customer data, real scanner exports, or private company information.

## 4. Disclosure Process

The project aims to follow this process:

```text

1. Acknowledge receipt of the report.

2. Assess impact and reproducibility.

3. Develop and test a fix.

4. Publish a coordinated security update when appropriate.

5. Credit the reporter when permission is provided.

```

Response timing may vary because this is an independently maintained publicly available, source-available project. No fixed response-time guarantee is made.

## 5. In Scope

Examples of security-relevant reports:

* Secret exposure through repository files, logs, diagnostics, or generated artifacts

* Unsafe Docker privilege configuration

* Docker socket exposure to application containers

* Command injection or unsafe subprocess handling

* Authentication or authorization flaws in future public endpoints

* Data-integrity bypasses that can create duplicate or unbalanced ledger records

* Evidence tampering that can incorrectly create a `GO` result

* Dependency or container image vulnerabilities with practical project impact

* Unsafe default network or database exposure

## 6. Out of Scope

The following are out of scope:

* Issues in unsupported forks or modified deployments

* Reports requiring access to private systems not owned by this project

* Social engineering

* Denial-of-service testing against systems without authorization

* Vulnerabilities in third-party services where this project has no control

* Reports based only on theoretical impact without a reproducible project-specific path

* Requests to include private enterprise configuration or internal integration details

## 7. Security Requirements for Contributors

Contributors must:

* Use synthetic data only.

* Never commit secrets or private configuration.

* Avoid privileged containers.

* Avoid mounting the Docker socket into application containers.

* Keep PostgreSQL private by default.

* Add or update tests for security-sensitive behavior.

* Update the threat model or ADRs when security boundaries change.

* Use dependency versions that can be reviewed and pinned.

## 8. Sensitive Artifact Handling

Generated evidence bundles, scanner results, logs, and diagnostics may contain sensitive technical details.

Do not commit generated artifacts unless they are intentionally synthetic, reviewed, and required as a test fixture.

The `artifacts/` directory is excluded from Git except for its `.gitkeep` placeholder.

## 9. Security References

Primary project security guidance:

* `docs/ENGINEERING_GUARDRAILS.md`

* `docs/THREAT_MODEL.md`

* `docs/ARCHITECTURE.md`

* `docs/INTEGRATION_CONTRACTS.md`
