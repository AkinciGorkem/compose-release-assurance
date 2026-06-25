\# Compose Release Assurance



Compose Release Assurance is an open-source, production-engineered reference framework for validating whether a Docker Compose-based stateful application is ready for release.



It combines quality, security, deployment, runtime health, recovery, and data-integrity evidence into one repeatable release rehearsal workflow.



> \*\*Project status:\*\* Pre-alpha. The repository is currently in the architecture and engineering-foundation phase.



\## Why This Project Exists



A successful build or green deployment job does not prove that a stateful release is operationally safe.



Before a release proceeds, engineering teams need evidence that:



\* The application starts correctly.

\* Dependencies are reachable and ready.

\* Health and readiness checks pass.

\* A restart does not create duplicate writes.

\* Database state remains valid after recovery scenarios.

\* Runtime metrics and diagnostics are available.

\* Quality and security evidence is visible.

\* The release can be classified as `GO`, `CONDITIONAL\_GO`, or `NO\_GO`.



Compose Release Assurance provides a structured way to execute these checks and create an auditable evidence bundle.



\## What It Is



\* A release-rehearsal framework for Docker Compose-based stateful services.

\* A reference implementation for secure, observable, testable, and recoverable delivery workflows.

\* A vendor-neutral evidence normalization layer.

\* A learning-oriented but engineering-focused open-source project.



\## What It Is Not



\* A replacement for CI/CD systems, registries, security scanners, monitoring platforms, or deployment tools.

\* A certified production platform for regulated financial environments.

\* A real payment system.

\* A repository containing real customer data, real credentials, private infrastructure data, or company-specific configurations.



\## Reference Application



The project will include a synthetic reference service named `ledger-api`.



It will demonstrate:



\* Transaction creation

\* PostgreSQL persistence

\* Idempotency-key support

\* Double-entry ledger records

\* Audit records

\* Health and readiness endpoints

\* Prometheus metrics



All data is synthetic. No real financial transaction or personal data is used.



\## Planned MVP



The first meaningful product milestone is:



```text

rehearsalctl rehearse --scenario api-restart

```



The command will:



1\. Start the Docker Compose stack.

2\. Validate application health and readiness.

3\. Create a synthetic transfer.

4\. Restart the API container in a controlled manner.

5\. Retry the request with the same idempotency key.

6\. Confirm that no duplicate transaction was created.

7\. Validate ledger integrity.

8\. Collect runtime diagnostics and metrics.

9\. Generate an evidence bundle.

10\. Return `GO` or `NO\_GO`.



\## Architecture Principles



This project follows the engineering rules defined in:



\* \[`docs/ENGINEERING\_GUARDRAILS.md`](docs/ENGINEERING\_GUARDRAILS.md)

\* \[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

\* \[`docs/THREAT\_MODEL.md`](docs/THREAT\_MODEL.md)

\* \[`docs/ACCEPTANCE\_CRITERIA.md`](docs/ACCEPTANCE\_CRITERIA.md)



Primary priorities are:



1\. Security and confidentiality

2\. Data integrity

3\. Safe failure and recovery

4\. Observability

5\. Maintainability

6\. Reproducibility

7\. Performance



\## Planned Technology Stack



```text

Application:        Python + FastAPI

Database:           PostgreSQL

Orchestration:      Docker Compose

Release CLI:        rehearsalctl

Deployment:         Ansible

Metrics:            Prometheus

Dashboards:         Grafana

Security scanning:  Grype

SBOM:               CycloneDX-compatible output

Quality tooling:    pytest, Ruff, mypy, pre-commit

CI reference:       Azure Pipelines

Registry reference: Nexus-compatible configuration

```



Enterprise integrations remain optional and vendor-neutral.



\## Repository Structure



```text

apps/               Reference applications

platform/           Rehearsal CLI and core platform logic

infra/              Docker Compose and infrastructure configuration

ansible/            Deployment, rollback, and diagnostics automation

observability/      Prometheus and Grafana configuration

policies/           Release-policy and evidence rules

scenarios/          Deterministic rehearsal scenarios

scripts/            Operational helper scripts

tests/              Automated test suites

docs/               Architecture, security, ADRs, and product documentation

artifacts/          Generated local evidence bundles; excluded from Git

```



\## Roadmap



\* \[x] Product vision and engineering guardrails

\* \[x] Architecture and threat model

\* \[x] Initial Architecture Decision Record

\* \[ ] Repository tooling and Python quality gates

\* \[ ] `ledger-api` reference service

\* \[ ] Docker Compose core stack

\* \[ ] API restart rehearsal scenario

\* \[ ] Integrity validation

\* \[ ] Prometheus and Grafana observability

\* \[ ] Evidence bundle generation

\* \[ ] Grype scan and SBOM support

\* \[ ] Ansible deployment and rollback

\* \[ ] Azure Pipelines reference workflow

\* \[ ] Public release documentation



\## Security and Confidentiality



Do not commit:



\* Credentials, tokens, certificates, SSH keys, or `.env` files

\* Internal URLs, IP addresses, hostnames, or pipeline details

\* Real logs, scanner reports, screenshots, or company artifacts

\* Customer, transaction, or personal data



Use synthetic data and example configuration files only.



Security guidance is documented in \[`docs/THREAT\_MODEL.md`](docs/THREAT\_MODEL.md).



\## Contributing



The project is under active development.



Before contributing, read:



\* \[`docs/ENGINEERING\_GUARDRAILS.md`](docs/ENGINEERING\_GUARDRAILS.md)

\* \[`docs/ACCEPTANCE\_CRITERIA.md`](docs/ACCEPTANCE\_CRITERIA.md)

\* \[`docs/adr/README.md`](docs/adr/README.md)



\## License



This project is licensed under the Apache License 2.0. See \[`LICENSE`](LICENSE).
