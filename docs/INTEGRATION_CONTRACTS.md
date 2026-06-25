\# Integration Contracts



\*\*Project:\*\* Compose Release Assurance

\*\*Document status:\*\* Draft v0.1

\*\*Purpose:\*\* Define vendor-neutral evidence contracts and adapter boundaries.



\## 1. Purpose



Compose Release Assurance does not replace CI/CD platforms, artifact registries, code-quality tools, security scanners, deployment automation, or monitoring platforms.



It consumes normalized evidence produced by those systems and combines that evidence with controlled runtime rehearsal results.



The core release-decision engine must remain independent from any specific vendor or private environment.



\## 2. Design Principles



All integrations must follow these rules:



\* The core domain must not directly depend on a vendor SDK, internal endpoint, private API, or company-specific configuration.

\* Every integration must be implemented behind an adapter boundary.

\* Adapters transform external data into a documented, normalized evidence contract.

\* Missing mandatory evidence must not silently become a success.

\* Raw reports may contain sensitive information and must not be committed to Git.

\* Public examples must use synthetic, redacted, or generated evidence only.

\* Live enterprise integration claims require authorized testing.



\## 3. Evidence Status Model



Every normalized evidence document must declare one of these statuses:



```text

PASS

WARN

FAIL

SKIPPED

UNKNOWN

```



Status meaning:



| Status    | Meaning                                                               |

| --------- | --------------------------------------------------------------------- |

| `PASS`    | Required validation completed successfully.                           |

| `WARN`    | Validation completed with a documented non-critical concern.          |

| `FAIL`    | Validation failed or policy threshold was exceeded.                   |

| `SKIPPED` | Validation was intentionally not executed and the reason is recorded. |

| `UNKNOWN` | Validation result cannot be trusted, parsed, or verified.             |



Mandatory evidence with `FAIL` or `UNKNOWN` must result in `NO\_GO`.



\## 4. Common Evidence Envelope



All evidence contracts will eventually conform to this conceptual structure:



```json

{

&#x20; "schema\_version": "1.0",

&#x20; "kind": "quality-gate",

&#x20; "source": {

&#x20;   "adapter": "sonarqube",

&#x20;   "source\_type": "external-tool",

&#x20;   "generated\_at": "2026-06-25T12:00:00Z"

&#x20; },

&#x20; "subject": {

&#x20;   "application": "ledger-api",

&#x20;   "release\_id": "example-release",

&#x20;   "artifact\_reference": "example.registry/ledger-api:1.0.0"

&#x20; },

&#x20; "status": "PASS",

&#x20; "summary": {

&#x20;   "message": "Quality gate passed",

&#x20;   "finding\_count": 0

&#x20; },

&#x20; "provenance": {

&#x20;   "collected\_by": "rehearsalctl",

&#x20;   "input\_checksum": "sha256:example"

&#x20; }

}

```



The exact JSON schemas will be defined under a future `schemas/` directory before adapters are implemented.



\## 5. Initial Adapter Map



| External capability           | Example tools                                         | Normalized output                             |

| ----------------------------- | ----------------------------------------------------- | --------------------------------------------- |

| Pipeline context              | Azure Pipelines, Jenkins                              | `pipeline-context.json`                       |

| Code quality                  | SonarQube Server                                      | `quality-gate.json`                           |

| Application security          | Fortify                                               | `security-findings.json`                      |

| Image and filesystem scanning | Grype                                                 | `security-findings.json`, `grype-report.json` |

| Artifact or image registry    | Nexus-compatible registry, Docker Hub, local registry | `artifact-manifest.json`                      |

| Deployment automation         | Ansible                                               | `deployment-result.json`                      |

| Runtime metrics               | Prometheus, Grafana                                   | `runtime-health.json`                         |

| External monitoring           | Dynatrace, Zabbix, SolarWinds                         | `runtime-health.json` or external summary     |

| External network scanning     | Nessus or approved security tooling                   | `external-security-summary.json`              |



\## 6. Adapter Responsibilities



An adapter must:



\* Validate required input fields.

\* Record source tool name and collection timestamp.

\* Normalize source status into the project status model.

\* Preserve non-sensitive summary details.

\* Reject malformed or oversized input safely.

\* Avoid exposing credentials, internal URLs, hostnames, tokens, or private report contents.

\* Produce actionable errors when evidence cannot be collected or parsed.



An adapter must not:



\* Make release decisions by itself.

\* Modify core business data.

\* Embed company-specific secrets or endpoints.

\* Treat unavailable evidence as `PASS`.

\* Commit raw enterprise reports to the repository.



\## 7. Initial Mandatory Evidence



The MVP requires evidence generated locally by the project:



```text

runtime-health.json

scenario-results.json

integrity-report.json

report.json

summary.md

checksums.sha256

```



The following are optional until their adapters are implemented and tested:



```text

pipeline-context.json

quality-gate.json

security-findings.json

artifact-manifest.json

deployment-result.json

external-security-summary.json

```



Optional evidence must be clearly marked as `SKIPPED` or `UNKNOWN`; it must never be represented as successfully validated.



\## 8. Release Policy Inputs



The release policy will evaluate evidence according to severity and mandatory status.



Examples:



```text

Health or readiness failure                  -> NO\_GO

Duplicate transaction                       -> NO\_GO

Ledger integrity failure                    -> NO\_GO

Missing mandatory rehearsal evidence        -> NO\_GO

Critical unresolved security finding        -> NO\_GO

Unavailable optional enterprise adapter     -> SKIPPED or CONDITIONAL\_GO

Quality gate failure when configured        -> NO\_GO

```



\## 9. Enterprise Compatibility Boundary



The project may provide compatible templates or adapters for enterprise tools, including Azure Pipelines, SonarQube Server, Fortify, Nexus-compatible registries, Ansible, Grafana, Jenkins, Dynatrace, Zabbix, SolarWinds, and Nessus.



Compatibility does not mean that the repository includes live access, private configuration, internal endpoints, or verified production integration with any organization.



\## 10. Future Work



Future versions may add:



\* JSON Schema validation

\* Signed evidence attestations

\* SBOM provenance verification

\* OPA or Conftest policy enforcement

\* Azure Pipelines templates

\* Jenkins pipeline examples

\* SonarQube and Fortify parser adapters

\* Ansible deployment-result adapter

\* Prometheus query adapter

\* Nexus-compatible artifact verification