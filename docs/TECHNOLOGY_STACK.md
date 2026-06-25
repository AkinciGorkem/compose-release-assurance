\# Technology Stack and Language Boundaries



\*\*Project:\*\* Compose Release Assurance

\*\*Document status:\*\* Draft v0.1

\*\*Purpose:\*\* Define the programming languages, declarative formats, and technology boundaries used by the project.



\## 1. Core Decision



Compose Release Assurance adopts a \*\*Python-first modular monolith\*\* approach.



Python is the primary implementation language for:



\* `ledger-api`

\* `rehearsalctl`

\* Release-policy evaluation

\* Evidence generation

\* Integrity validation

\* Enterprise evidence adapters

\* Automated tests

\* Local developer tooling



The project avoids unnecessary polyglot architecture during the MVP.



\## 2. Primary Runtime



\### Python



\*\*Baseline runtime:\*\* Python 3.12



Python will be used for all core executable product logic.



It provides one consistent language for API development, command-line orchestration, test automation, JSON evidence processing, integration adapters, diagnostics, and policy evaluation.



The exact patch version and container image digest will be pinned when the reproducible development environment is created.



\## 3. Language and Format Matrix



| Area                      | Language or format                | Responsibility                                                             |

| ------------------------- | --------------------------------- | -------------------------------------------------------------------------- |

| `apps/ledger-api/`        | Python                            | API endpoints, domain rules, validation, health, readiness, metrics        |

| `platform/rehearsalctl/`  | Python                            | CLI commands, Compose orchestration, scenarios, evidence, release decision |

| `tests/`                  | Python                            | Unit, integration, contract, and end-to-end rehearsal tests                |

| PostgreSQL schema         | SQL                               | Tables, constraints, transactions, indexes, integrity safeguards           |

| Database migrations       | Python and SQL                    | Controlled schema evolution                                                |

| `infra/compose/`          | YAML and Dockerfile               | Docker Compose services, networks, volumes, health checks, images          |

| `ansible/`                | YAML and limited Jinja templating | Deployment, rollback, host preparation, diagnostics                        |

| Azure Pipelines templates | YAML                              | CI/CD reference stages, jobs, artifacts, and quality gates                 |

| Prometheus configuration  | YAML                              | Metric scrape configuration                                                |

| Grafana dashboards        | JSON and YAML                     | Dashboard definitions and provisioning                                     |

| `scripts/`                | Bash                              | Linux-only backup, restore, diagnostics, and cleanup helpers               |

| Local Windows bootstrap   | PowerShell                        | Developer convenience only; not core product runtime                       |

| Evidence contracts        | JSON                              | Machine-readable evidence, schemas, adapters, results                      |

| Human-readable evidence   | Markdown                          | Release summary and diagnostics overview                                   |

| Future static reports     | HTML and CSS                      | Read-only human-facing report output                                       |

| Documentation             | Markdown                          | Architecture, security, ADRs, runbooks, contribution guidance              |



\## 4. API Implementation Policy



The synthetic `ledger-api` will use Python and FastAPI.



The API must provide:



```text

POST /transfers

GET /transfers/{reference\_id}

GET /health

GET /ready

GET /metrics

```



The MVP must prioritize correctness and observability over theoretical throughput.



The initial database access model will be synchronous.



The project must not introduce asynchronous database access until measurement demonstrates a concrete need and an ADR records the decision.



No blocking database or Docker operation may run inside an asynchronous request path.



\## 5. CLI Implementation Policy



`rehearsalctl` will be a Python CLI.



It will manage:



```text

validate

up

down

rehearse

collect

report

verify

```



The CLI must:



\* Use explicit command arguments.

\* Avoid unsafe shell-string interpolation.

\* Use bounded subprocess timeouts.

\* Return deterministic process exit codes.

\* Produce actionable error messages.

\* Keep Docker and Compose interactions outside application containers.

\* Preserve evidence before destructive cleanup.



The exact CLI library is intentionally deferred until the Python quality foundation is established.



\## 6. SQL and Database Policy



PostgreSQL is the only MVP database.



SQL must enforce critical integrity safeguards where appropriate.



The application must not rely solely on Python validation for:



```text

Idempotency uniqueness

Foreign-key integrity

Transaction atomicity

Ledger balance consistency

Audit record relationships

```



Database migration design will be documented before schema implementation begins.



\## 7. Declarative Infrastructure Policy



YAML is used for configuration and orchestration, not for core business logic.



YAML files may define:



```text

Docker Compose services

Ansible playbooks

Azure Pipelines workflows

Prometheus configuration

Release-policy thresholds

Scenario metadata

```



Complex decision logic must remain in tested Python code.



\## 8. Bash and PowerShell Boundaries



\### Bash



Bash is limited to Linux and WSL operational helper scripts.



Examples:



```text

Database backup

Database restore

Diagnostic collection

Artifact cleanup

Log handling

Host prerequisite checks

```



All Bash scripts must use:



```bash

set -Eeuo pipefail

```



\### PowerShell



PowerShell is limited to local Windows developer setup and repository commands.



PowerShell must not contain core release policy, business rules, integrity validation, or production deployment logic.



\## 9. Explicit MVP Exclusions



The MVP will not use:



```text

JavaScript

TypeScript

React

Next.js

C#

Go

Kubernetes

Terraform

HCL

Message queues

Distributed microservices

AI agents

```



These technologies may be evaluated only when a documented product requirement justifies them.



\## 10. Technology Selection Rules



A new language, framework, service, or dependency may be introduced only when:



```text

A documented problem exists.

The existing stack cannot solve it safely or maintainably.

Security impact is reviewed.

Operational impact is reviewed.

Testing strategy is defined.

Rollback or removal is possible.

An ADR is created when the change is architecturally significant.

```



\## 11. Session Instruction



For development sessions involving implementation decisions, use:



```text

Read docs/ENGINEERING\_GUARDRAILS.md and docs/TECHNOLOGY\_STACK.md first.



Treat both documents as binding engineering guidance. Preserve the Python-first modular monolith approach. Do not introduce a language, framework, service, dependency, or asynchronous architecture without a documented problem, security review, operational review, test plan, and—when significant—an ADR.

```