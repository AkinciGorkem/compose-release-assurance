\# Acceptance Criteria



\*\*Project:\*\* Compose Release Assurance

\*\*Document status:\*\* Draft v0.1



\## 1. Delivery Principle



A feature is complete only when it is implemented, tested, observable, documented, and recoverable according to `ENGINEERING\_GUARDRAILS.md`.



A working happy-path demo alone is not sufficient.



\## 2. MVP Definition



The MVP is complete when the project can execute:



```text

rehearsalctl rehearse --scenario api-restart

```



and produce a deterministic release decision with evidence.



\## 3. MVP Functional Acceptance Criteria



\### 3.1 Reference Stack



\* The stack contains `ledger-api` and PostgreSQL.

\* The stack starts using Docker Compose.

\* PostgreSQL is not publicly exposed by default.

\* The API provides `/health`, `/ready`, and `/metrics`.

\* The API runs as a non-root user where practical.

\* The stack uses explicit image tags rather than `latest` in release-oriented configuration.



\### 3.2 Transaction Integrity



\* A transfer request requires an idempotency key.

\* Repeating the same request with the same idempotency key does not create duplicate records.

\* Every successful transfer creates balanced debit and credit ledger records.

\* Every successful transfer creates an audit record.

\* Integrity validation detects duplicate or unbalanced records.

\* Any integrity failure results in `NO\_GO`.



\### 3.3 API Restart Rehearsal



\* The rehearsal command starts the stack or verifies that it is ready.

\* The command creates a synthetic transfer.

\* The API container is restarted in a controlled manner.

\* The original request is retried with the same idempotency key.

\* The command verifies that no duplicate transfer was created.

\* The command records restart and recovery evidence.

\* The command exits with code `0` only when mandatory checks pass.



\### 3.4 Runtime Evidence



The rehearsal output must include:



```text

runtime-health.json

scenario-results.json

integrity-report.json

summary.md

report.json

checksums.sha256

```



Evidence must include:



\* Container state

\* Health and readiness result

\* Scenario start and end time

\* Release decision

\* Integrity result

\* Relevant diagnostic information

\* SHA-256 checksums



\### 3.5 Observability



\* Prometheus collects API metrics.

\* Grafana provides a release-health dashboard.

\* At minimum, metrics include request count, error count, latency, readiness state, and recovery duration.

\* Logs must not expose credentials, tokens, or secrets.



\### 3.6 Security Baseline



\* No secrets are committed to Git.

\* `.env.example` contains placeholders only.

\* Grype scanning can produce a security report.

\* An SBOM can be generated.

\* A critical unresolved security finding produces `NO\_GO`.

\* The project documents how enterprise quality and security evidence can be normalized without requiring live access to enterprise systems.



\### 3.7 Documentation



The repository must include:



```text

README.md

docs/ENGINEERING\_GUARDRAILS.md

docs/PRODUCT\_VISION.md

docs/ACCEPTANCE\_CRITERIA.md

docs/architecture.md

docs/threat-model.md

docs/integration-contracts.md

docs/adr/

```



\## 4. Non-Functional Acceptance Criteria



\### Maintainability



\* Python code passes formatting, linting, and type checks.

\* New behavior is covered by automated tests.

\* Major decisions are recorded as ADRs.

\* Scripts are readable, documented, and use safe shell practices.



\### Reliability



\* Critical operations use bounded timeouts and retries.

\* Failure paths provide actionable messages.

\* Cleanup behavior is documented.

\* The system does not silently ignore failed validation.



\### Security



\* No privileged containers.

\* No Docker socket mount in application containers.

\* Database access remains internal by default.

\* Public examples use synthetic data only.



\### Performance



\* Performance claims must be backed by measurements.

\* The project records recovery duration.

\* The API must avoid obvious blocking operations in critical request paths.

\* Resource usage must be visible through diagnostics and monitoring.



\## 5. Release Decision Criteria



\### GO



All mandatory checks pass.



\### CONDITIONAL\_GO



A non-critical issue exists, is documented, and has an explicit approval or waiver in the evidence bundle.



\### NO\_GO



Any mandatory failure exists, including:



```text

Health failure

Readiness failure

Duplicate transaction

Unbalanced ledger

Backup or restore failure

Critical unresolved security finding

Missing mandatory evidence

Invalid checksum manifest

```



\## 6. Definition of Done for Every Work Item



A work item is complete only when:



\* Acceptance criteria are met.

\* Relevant unit or integration tests pass.

\* Security implications are reviewed.

\* Logs, metrics, and diagnostics are considered.

\* Failure and recovery behavior are defined.

\* Documentation is updated.

\* No critical unresolved issue remains hidden.