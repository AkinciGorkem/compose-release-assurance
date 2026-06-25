\# Contributing to Compose Release Assurance



Thank you for contributing to Compose Release Assurance.



This project values trustworthy engineering over superficial complexity. Contributions must improve security, data integrity, reliability, observability, maintainability, documentation, or reproducibility.



\## 1. Before You Start



Read these documents before proposing a change:



\* `docs/ENGINEERING\_GUARDRAILS.md`

\* `docs/PRODUCT\_VISION.md`

\* `docs/ACCEPTANCE\_CRITERIA.md`

\* `docs/ARCHITECTURE.md`

\* `docs/THREAT\_MODEL.md`

\* `docs/INTEGRATION\_CONTRACTS.md`

\* `docs/adr/README.md`



Large changes that affect architecture, persistence, security, deployment, observability, or release policy require discussion before implementation.



\## 2. Contribution Scope



Useful contributions include:



\* Bug fixes

\* Security improvements

\* Tests

\* Documentation improvements

\* Deterministic rehearsal scenarios

\* Evidence-contract adapters

\* Metrics and diagnostics

\* Docker Compose hardening

\* Ansible automation

\* Accessibility and usability improvements

\* Reproducibility improvements



Out-of-scope contributions include:



\* Real financial integrations

\* Real customer data

\* Private infrastructure configuration

\* Company-specific endpoints or credentials

\* Unreviewed third-party binaries

\* Features that add complexity without a documented problem



\## 3. Security and Confidentiality



Never commit:



\* Passwords, tokens, API keys, certificates, SSH keys, `.env` files, or private configuration

\* Internal URLs, IP addresses, hostnames, pipeline details, scanner exports, or raw monitoring data

\* Customer data, personal data, real transaction data, or internal company information

\* Screenshots from private systems



Use synthetic data and example configuration files only.



Potential security vulnerabilities must not be reported through public GitHub issues. Read `SECURITY.md` for responsible disclosure instructions.



\## 4. Work Item Standard



Every change must define:



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



Keep work items small enough to review, test, and revert safely.



\## 5. Branch Naming



Use descriptive branch names:



```text

feat/api-restart-scenario

fix/idempotency-duplicate-check

docs/integration-contracts

security/redact-diagnostics

test/ledger-integrity

refactor/evidence-builder

```



\## 6. Commit Messages



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



Examples:



```text

feat: add API restart rehearsal scenario

fix: reject duplicate idempotency key writes

docs: clarify evidence status model

security: redact sensitive diagnostic fields

test: cover ledger balance validation

```



\## 7. Quality Requirements



Before submitting a change:



```text

Formatting passes

Linting passes

Type checks pass

Relevant unit tests pass

Relevant integration tests pass

Security implications are reviewed

Documentation is updated

Acceptance criteria are met

```



A happy-path demonstration alone is not sufficient.



\## 8. Architecture Decision Records



Create or update an ADR when a change affects:



\* Security or confidentiality

\* Data integrity

\* Public interfaces

\* Persistent storage

\* Deployment architecture

\* Docker privileges

\* Observability

\* Recovery or rollback behavior

\* Enterprise-tool integration

\* Release decision policy



ADR files belong under `docs/adr/`.



\## 9. Pull Request Expectations



A pull request should include:



\* Clear problem statement

\* Scope and non-goals

\* Test evidence

\* Security considerations

\* Operational impact

\* Documentation updates

\* Recovery or rollback notes

\* Screenshots only when they contain synthetic and non-sensitive data



Avoid unrelated formatting, refactoring, or dependency changes in the same pull request.



\## 10. Review Standard



A contribution may be rejected or asked to change when it:



\* Introduces unnecessary complexity

\* Weakens security boundaries

\* Hides failures

\* Makes release decisions less conservative

\* Reduces testability or observability

\* Adds unreviewed dependencies

\* Contains confidential or sensitive information

\* Lacks documentation or recovery behavior



\## 11. Community Conduct



Be respectful, specific, and constructive.



Focus discussions on technical evidence, user impact, security, reliability, and maintainability. Personal attacks, harassment, discriminatory language, or disclosure of confidential information are not accepted.
