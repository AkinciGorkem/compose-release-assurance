# ADR-0002: Adopt a Python-First Runtime and Explicit Language Boundaries

**Status:** Accepted

**Date:** 2026-06-25
> **Superseded in part:** The Python minor-version baseline in this ADR is superseded by [ADR-0003](0003-python-314-runtime-baseline.md). The Python-first language-boundary decision remains accepted.

## Context

Compose Release Assurance requires:

* A synthetic REST API

* A command-line release orchestration tool

* Docker Compose control

* Evidence collection and normalization

* Security and quality adapter support

* Automated tests

* Database integrity validation

* Ansible and Azure Pipelines integration references

Using multiple implementation languages during the MVP would increase build complexity, onboarding cost, dependency management, test duplication, CI complexity, and security review surface.

The project must remain understandable to public contributors while demonstrating production-oriented engineering practices.

## Decision

The project adopts Python 3.12 as the primary implementation runtime.

Python will be used for:

* `ledger-api`

* `rehearsalctl`

* Integrity validation

* Evidence builder

* Scenario runner

* Release-policy engine

* Integration adapters

* Tests and developer tooling

Declarative and specialized languages are limited to their appropriate boundaries:

* SQL for PostgreSQL schema and integrity constraints

* YAML for Docker Compose, Ansible, Azure Pipelines, Prometheus configuration, and scenario metadata

* Bash for Linux operational helper scripts

* PowerShell for local Windows developer bootstrap only

* JSON for machine-readable evidence contracts

* Markdown for documentation

* HTML and CSS for future static report rendering

## Consequences

### Positive

* One primary language for product logic, testing, adapters, and automation.

* Lower cognitive load for contributors.

* Clear separation between business logic and infrastructure configuration.

* Easier quality-gate and dependency management.

* Better reuse of validation, logging, error handling, and evidence models.

* Simpler public repository onboarding.

### Negative

* The project does not demonstrate multiple backend languages.

* Some future integrations may have stronger native libraries in another ecosystem.

* Python runtime performance must be measured and monitored rather than assumed.

* The team must resist adding asynchronous complexity without a demonstrated requirement.

## Alternatives Considered

### C# and .NET

Rejected for MVP.

C# is a strong enterprise option, but selecting it would require rewriting the planned Python API and CLI approach. Mixing C# with Python would increase complexity without delivering a required product benefit.

### Go

Rejected for MVP.

Go is suitable for systems programming and CLI tools. However, it would add learning, implementation, testing, and maintenance cost without solving a proven MVP requirement.

### JavaScript or TypeScript

Rejected for MVP.

The project has no browser-based management interface in scope. Adding a Node.js runtime would create unnecessary dependency and CI complexity.

### Polyglot architecture

Rejected for MVP.

Multiple implementation languages would increase operational and security review surface while reducing repository simplicity.

## Security Impact

* Fewer runtime ecosystems reduce dependency and supply-chain surface.

* Core policy and integrity logic remain in one testable language.

* Bash and PowerShell are restricted from owning business or release-decision logic.

* YAML remains declarative and does not replace tested Python validation.

## Operational Impact

* Contributors need one primary runtime: Python.

* CI requires one primary language toolchain.

* Docker images can use a consistent Python base image strategy.

* Development, testing, and troubleshooting workflows become more uniform.

## Rollback Plan

This decision may be revisited only when a specific requirement cannot be met safely or maintainably with the current Python-first approach.

Any future change introducing another primary runtime requires:

```text

Documented problem

Alternatives analysis

Security review

Operational review

Testing strategy

Migration plan

ADR approval

```
