# Architecture Decision Records

Architecture Decision Records, abbreviated as ADRs, document important technical and operational decisions made in this repository.

An ADR is required when a decision affects:

* Security or confidentiality

* Data integrity

* Public interfaces

* Persistent storage

* Deployment architecture

* Observability

* Release policy

* Infrastructure privileges

* Third-party or enterprise-tool integration

* Recovery or rollback behavior

## Status Values

```text

Proposed

Accepted

Deprecated

Superseded

Rejected

```

## Naming Convention

ADR files use this format:

```text

NNNN-short-decision-title.md

```

Example:

```text

0001-host-cli-orchestration.md

```

Numbers are sequential and must not be reused.

## ADR Template

```text

# ADR-NNNN: Decision Title

**Status:** Proposed

**Date:** YYYY-MM-DD

## Context

Describe the problem, constraints, and decision drivers.

## Decision

Describe the selected approach.

## Consequences

### Positive

### Negative

## Alternatives Considered

## Security Impact

## Operational Impact

## Rollback Plan

```

## ADR Index

| ADR                                        | Status   | Summary                                                                                                                      |

| ------------------------------------------ | -------- | ---------------------------------------------------------------------------------------------------------------------------- |

| [ADR-0001](0001-host-cli-orchestration.md) | Accepted | Release orchestration runs on an authorized host or CI runner instead of an application container with Docker socket access. |
| [ADR-0002](0002-python-first-runtime-and-language-boundaries.md) | Accepted | Python is the primary runtime; SQL, YAML, Bash, PowerShell, JSON, Markdown, and HTML/CSS have explicit boundaries. |
| [ADR-0003](0003-python-314-runtime-baseline.md) | Accepted | Python 3.14 is the initial supported runtime; other Python versions require automated compatibility validation before support is claimed. |
| [ADR-0004](0004-source-available-no-sale-license-policy.md) | Accepted | The project is public and source-available under Apache-2.0 with Commons Clause 1.0; resale and substantially equivalent paid offerings are restricted. |
| [ADR-0005](0005-postgresql-relational-ledger-persistence-baseline.md) | Accepted | PostgreSQL uses versioned plain-SQL migrations and relational constraints; the future adapter owns transactional writes and safe replay. |
