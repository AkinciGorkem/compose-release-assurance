\# Architecture Decision Records



Architecture Decision Records, abbreviated as ADRs, document important technical and operational decisions made in this repository.



An ADR is required when a decision affects:



\* Security or confidentiality

\* Data integrity

\* Public interfaces

\* Persistent storage

\* Deployment architecture

\* Observability

\* Release policy

\* Infrastructure privileges

\* Third-party or enterprise-tool integration

\* Recovery or rollback behavior



\## Status Values



```text

Proposed

Accepted

Deprecated

Superseded

Rejected

```



\## Naming Convention



ADR files use this format:



```text

NNNN-short-decision-title.md

```



Example:



```text

0001-host-cli-orchestration.md

```



Numbers are sequential and must not be reused.



\## ADR Template



```text

\# ADR-NNNN: Decision Title



\*\*Status:\*\* Proposed

\*\*Date:\*\* YYYY-MM-DD



\## Context



Describe the problem, constraints, and decision drivers.



\## Decision



Describe the selected approach.



\## Consequences



\### Positive



\### Negative



\## Alternatives Considered



\## Security Impact



\## Operational Impact



\## Rollback Plan

```



\## ADR Index



| ADR                                        | Status   | Summary                                                                                                                      |

| ------------------------------------------ | -------- | ---------------------------------------------------------------------------------------------------------------------------- |

| \[ADR-0001](0001-host-cli-orchestration.md) | Accepted | Release orchestration runs on an authorized host or CI runner instead of an application container with Docker socket access. |