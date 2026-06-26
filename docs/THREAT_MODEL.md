# Threat Model

**Project:** Compose Release Assurance

**Document status:** Draft v0.1

**Scope:** Public, source-available reference implementation, local development, controlled CI, and authorized rehearsal environments

## 1. Security Objective

The project must safely validate release readiness without exposing secrets, internal infrastructure details, sensitive logs, or real financial data.

The framework must prefer a conservative `NO_GO` outcome over an unsupported or unverifiable `GO` result.

## 2. Protected Assets

| Asset                                       | Why it matters                                                   |

| ------------------------------------------- | ---------------------------------------------------------------- |

| Credentials, tokens, certificates, SSH keys | Unauthorized infrastructure or registry access                   |

| Docker host access                          | Docker control can become host-level privilege                   |

| Database state                              | Integrity of transfer, ledger, idempotency, and audit records    |

| Evidence bundle                             | Basis for release decision and later investigation               |

| CI pipeline context                         | May contain environment or deployment metadata                   |

| Security reports                            | May reveal vulnerabilities, paths, versions, or internal details |

| Source code and public repository           | Must not expose company or personal confidential information     |

| Monitoring data and logs                    | May accidentally include sensitive values                        |

## 3. Trust Boundaries

```text

Public Git repository

        |

Developer workstation / CI runner

        |

Docker Engine and Compose environment

        |

Application and database network

        |

External quality, security, registry, deployment, and monitoring evidence

```

Each boundary must validate inputs and avoid implicit trust.

## 4. Threats and Controls

| Threat                                   | Example                                                     | Primary controls                                                                             |

| ---------------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------- |

| Secret exposure                          | `.env`, token, private key, scanner output committed to Git | `.gitignore`, example files only, secret scanning, review before commit                      |

| Docker privilege escalation              | Container receives Docker socket or privileged mode         | No Docker socket in application containers, no privileged containers, host CLI orchestration |

| Image supply-chain risk                  | Mutable image tag or vulnerable dependency                  | Pinned tags, Grype scan, SBOM, digest recording                                              |

| Evidence tampering                       | Edited report falsely indicates success                     | Checksums, timestamps, source metadata, schema validation                                    |

| False GO decision                        | Missing check treated as success                            | Mandatory checks fail closed, explicit skipped-state handling                                |

| Duplicate transaction                    | Retry after restart creates a second transfer               | Idempotency key, database constraint, transactional writes, integrity validator              |

| Ledger imbalance                         | Partial write creates debit without credit                  | Atomic database transaction, invariant checks                                                |

| Database exposure                        | PostgreSQL port exposed on host                             | Internal network by default, no public database port in release config                       |

| Command injection                        | Unsafe shell or subprocess handling                         | Avoid shell interpolation, validate inputs, bounded command interfaces                       |

| Unsafe Ansible execution                 | Inventory or playbook targets unintended host               | Explicit inventory, SSH keys, least privilege, dry-run support where appropriate             |

| Resource exhaustion                      | Container consumes CPU, memory, disk, or log storage        | Resource limits, health checks, diagnostics, log rotation strategy                           |

| Sensitive logging                        | Password, token, or full payload appears in logs            | Structured logging, redaction, synthetic data, review log fields                             |

| Dependency outage                        | Database or API unavailable during rehearsal                | Timeouts, bounded retries, readiness checks, explicit NO_GO                                  |

| Malicious evidence file                  | Crafted JSON exploits parser or causes misleading result    | Schema validation, file-size limits, strict parsing                                          |

| Public branding or confidentiality issue | Company details included in public repository               | Vendor-neutral wording, no internal names, endpoints, logs, or screenshots                   |

## 5. STRIDE Summary

| Category               | Relevant risks                                                              |

| ---------------------- | --------------------------------------------------------------------------- |

| Spoofing               | Fake pipeline context, fake security report, unauthorized deployment target |

| Tampering              | Modified evidence, altered Compose files, manipulated artifact metadata     |

| Repudiation            | Missing timestamps, missing checksums, unclear scenario provenance          |

| Information disclosure | Secrets, internal URLs, logs, scanner findings, personal information        |

| Denial of service      | Resource exhaustion, infinite retry, runaway logs, unavailable dependencies |

| Elevation of privilege | Docker socket access, privileged container, unsafe Ansible credentials      |

## 6. Mandatory Security Controls for MVP

```text

No committed secrets

Synthetic data only

Non-root application container where practical

No privileged container

No Docker socket mount in application containers

Private PostgreSQL network

Health and readiness checks

Bounded retries and timeouts

Transactional database writes

Idempotency validation

Grype scan support

SBOM generation support

Checksum manifest for evidence bundles

Structured logging with redaction

```

## 7. Security Controls Deferred Beyond MVP

```text

Signed container images

SBOM attestation and provenance verification

Policy-as-code enforcement through OPA / Conftest

Centralized secret-management integration

Runtime container-security monitoring

Network-policy enforcement

External penetration-testing evidence ingestion

Enterprise SSO and RBAC

Multi-tenant authorization model

```

## 8. Security Review Triggers

A threat-model update and ADR review are required when any of these change:

* New external service or registry integration

* New secret type or credential flow

* New network exposure

* New persistent storage

* New deployment target

* Docker socket usage proposal

* New privileged operation

* New evidence source

* New public API endpoint

* New recovery or backup mechanism

## 9. Incident and Failure Handling

When an integrity, health, security, or evidence failure occurs:

```text

1. Stop release approval.

2. Mark the result as NO_GO unless an explicit policy states otherwise.

3. Collect redacted diagnostics.

4. Preserve evidence with checksums.

5. Provide actionable failure context.

6. Avoid automatic destructive cleanup before evidence collection completes.

```

## 10. Non-Goals

This threat model does not claim to certify the project for use in a regulated production environment.

A real organizational deployment would additionally require:

```text

Formal security review

Penetration testing

Access-control design

Secret-management review

Compliance review

Data-retention policy

Incident-response process

Operational ownership

Change-management approval

```
