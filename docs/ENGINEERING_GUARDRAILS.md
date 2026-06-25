# Engineering Guardrails

**Project:** Compose Release Assurance
**Status:** Draft v0.1
**Purpose:** Governing engineering contract for all product, architecture, code, infrastructure, security, testing, documentation, and operational decisions.

---

## 1. Product Standard

This project is a **production-engineered reference implementation**, not a claim of being production-certified software.

The goal is to provide a reusable, secure, observable, testable, and recoverable release-assurance workflow for Docker Compose-based stateful services.

The project must remain:

* Useful without relying on a specific company, vendor, or private environment.
* Safe to publish as open source.
* Free of real customer data, real credentials, internal endpoints, company source code, internal logs, or confidential infrastructure details.
* Designed for synthetic financial-event data only.
* Explainable to engineers, managers, security teams, and open-source contributors.

---

## 2. Decision Priority

When trade-offs exist, decisions follow this order:

1. Security and confidentiality
2. Data correctness and integrity
3. Safe failure and recovery
4. Operability and observability
5. Maintainability and readability
6. Performance and latency
7. Feature delivery speed

A feature must not be accepted merely because it works in a happy-path demo.

---

## 3. Core Engineering Principles

### 3.1 Keep the design simple

* Prefer clear, direct, maintainable solutions over clever abstractions.
* Do not add a framework, service, database, queue, plugin, or dependency unless it solves a documented problem.
* Avoid premature microservices, Kubernetes, Terraform modules, AI agents, and distributed systems complexity.
* Build vertical slices: one small feature must be functional, tested, observable, documented, and recoverable before moving to the next one.

### 3.2 Apply SOLID pragmatically

* Each module has one clear responsibility.
* Business rules must not depend directly on Docker, HTTP, database, Azure DevOps, Nexus, SonarQube, Fortify, or Grafana.
* Infrastructure dependencies must be isolated behind explicit interfaces or adapters.
* Do not create abstractions that have only one obvious implementation unless a real extension point exists.
* Public interfaces must be small, explicit, documented, and tested.

### 3.3 Clean code rules

* Use meaningful names; avoid unexplained abbreviations.
* Keep functions focused and short where practical.
* Validate inputs at system boundaries.
* Return explicit errors with actionable context.
* Remove dead code, unused dependencies, debug prints, and temporary workarounds before merging.
* Comments explain why, not what obvious code already says.
* No silent failure paths.

---

## 4. Reliability and Data Integrity

### 4.1 Failure handling

The system must assume that containers, networks, storage, processes, and dependencies can fail.

Every critical operation must define:

* Timeout
* Retry policy
* Retry limit
* Backoff behavior
* Failure result
* Recovery behavior
* Evidence collected after failure

Retries must never create duplicate financial events or duplicate ledger entries.

### 4.2 Idempotency

All write operations that may be retried must support idempotency.

For the demo ledger service:

* The same idempotency key must not create duplicate transfers.
* Database writes must be transactional.
* Ledger invariants must be validated after every rehearsal scenario.
* A failed or uncertain integrity check results in `NO_GO`.

### 4.3 Safe release decision

The release decision is conservative:

```text
GO              = all mandatory gates passed
CONDITIONAL_GO  = non-critical exception exists and is explicitly documented
NO_GO           = security, integrity, health, recovery, or evidence requirement failed
```

Missing evidence is not a success state.

---

## 5. Security Baseline

* Never commit secrets, tokens, passwords, certificates, SSH private keys, `.env` files, scanner reports containing sensitive details, or internal URLs.
* Use `.env.example`, `config.example.yaml`, and placeholder values only.
* Use synthetic data only.
* Run containers as non-root whenever practical.
* Apply least privilege: no privileged containers, no unnecessary Linux capabilities, no unnecessary host mounts.
* Do not mount the Docker socket into application containers.
* Keep databases private by default; do not expose database ports to the host unless a documented local-only use case requires it.
* Pin dependency versions and container image versions where practical.
* Scan images and filesystems using Grype.
* Generate an SBOM.
* Treat SonarQube, Fortify, Nessus, Dynatrace, Zabbix, SolarWinds, Nexus, Azure DevOps, and Jenkins as optional enterprise integrations through adapters or evidence contracts unless real authorized access exists.
* Never claim that a specific enterprise tool is actively integrated unless it has been tested in an authorized environment.

---

## 6. Performance and Resilience

* Measure before optimizing.
* Define latency and timeout expectations for critical API and rehearsal operations.
* Avoid blocking I/O in request paths where asynchronous or bounded alternatives are appropriate.
* Use bounded retries, not infinite loops.
* Apply resource limits in Docker Compose where supported.
* Add health checks and readiness checks.
* Ensure services fail clearly and recover predictably.
* Prefer graceful shutdown and explicit cleanup.
* Record recovery duration as a metric and rehearsal result.

---

## 7. Observability Rules

Every core service must provide:

* Structured logs
* Health endpoint
* Readiness endpoint
* Metrics endpoint
* Correlation or request identifier where relevant
* Clear error categories
* Redaction of secrets and sensitive values

Observability must include:

* Request rate
* Error rate
* Latency
* Restart count
* Readiness state
* Recovery duration
* Database connectivity
* Rehearsal scenario result
* Integrity validation result

Logs must never contain passwords, access tokens, secrets, or unnecessary sensitive transaction details.

---

## 8. Testing and Quality Gates

Every feature must include appropriate tests.

Testing order:

1. Unit tests for business rules
2. Integration tests for database and service boundaries
3. End-to-end rehearsal tests for critical workflows
4. Failure and recovery tests for release scenarios

Mandatory quality gates before a feature is considered complete:

```text
- Formatting passes
- Linting passes
- Type checks pass
- Unit tests pass
- Relevant integration tests pass
- Security scan is reviewed
- Documentation is updated
- Acceptance criteria are met
```

The initial Python toolchain will use:

```text
pytest
ruff
mypy
pre-commit
```

---

## 9. Docker and Infrastructure Rules

* Use multi-stage Docker builds where beneficial.
* Keep images minimal and reproducible.
* Use explicit health checks.
* Avoid `latest` tags in release-oriented Compose definitions.
* Separate application, database, observability, and optional tooling through Compose profiles or explicit services.
* Keep PostgreSQL on an internal network by default.
* Persist state through named volumes only where necessary.
* Document backup, restore, cleanup, and rollback behavior.
* All Bash scripts must use safe shell practices, including:

```bash
set -Eeuo pipefail
```

* Scripts must be idempotent where possible.
* Scripts must validate prerequisites and fail with actionable errors.

---

## 10. Delivery and Enterprise Compatibility

The project will provide vendor-neutral evidence contracts.

Examples:

```text
quality-gate.json
security-findings.json
grype-report.json
sbom.cdx.json
pipeline-context.json
deployment-result.json
runtime-health.json
scenario-results.json
integrity-report.json
```

Enterprise-compatible references may include:

```text
Azure DevOps Pipelines
SonarQube Server
Fortify
Nexus-compatible registry
Ansible
Grafana
Jenkins
Terraform
```

These integrations must remain optional and configurable.

---

## 11. Agile Delivery Model

Work is performed in small, reviewable slices.

Each work item must define:

```text
Problem
Scope
Out of scope
Acceptance criteria
Security considerations
Operational considerations
Tests required
Documentation required
Rollback or recovery behavior
```

Definition of Ready:

```text
- Problem is understood
- Acceptance criteria are written
- Dependencies are known
- Security risks are identified
- Scope is small enough to complete and test
```

Definition of Done:

```text
- Code is complete
- Tests pass
- Quality gates pass
- Documentation is updated
- Logs/metrics are considered
- Security implications are reviewed
- Failure behavior is defined
- No known critical issue remains undocumented
```

---

## 12. Architecture and Change Control

Architecture decisions that affect security, data integrity, interfaces, deployment, persistence, or observability must be recorded as ADRs under:

```text
docs/adr/
```

Each ADR must include:

```text
Context
Decision
Alternatives considered
Consequences
Security impact
Operational impact
Rollback plan
```

Use Conventional Commits:

```text
feat:
fix:
docs:
test:
refactor:
build:
ci:
chore:
security:
```

---

## 13. Session Instruction for AI-Assisted Development

For every new development session, provide this instruction:

```text
Read docs/ENGINEERING_GUARDRAILS.md first.
Treat it as the governing contract.
Do not introduce unnecessary complexity.
Preserve security, data integrity, observability, testability, recoverability, clean architecture, and documentation quality.
Before proposing code, state the scope, acceptance criteria, risks, tests, operational impact, and rollback or recovery behavior.
```

---

## 14. Stop-the-Line Rule

Do not continue to the next feature when any of these are unresolved:

```text
- Failing tests
- Unexplained security finding
- Broken health or readiness check
- Missing rollback or recovery behavior
- Integrity uncertainty
- Undocumented breaking change
- Secret exposure risk
- Incomplete evidence output
```

Resolve, document, or explicitly defer the issue with a tracked reason before proceeding.

---

## 15. Project Ethos

This project prioritizes trustworthy engineering over superficial complexity.

A smaller, complete, secure, observable, tested, documented, and recoverable feature is more valuable than a large unfinished feature set.

The standard is not “does it run once?”

The standard is:

> Can another engineer understand it, run it, test it, diagnose it, recover it, trust its evidence, and extend it safely?
