# ADR-0001: Run Release Orchestration from an Authorized Host or CI Runner

**Status:** Accepted

**Date:** 2026-06-25

## Context

Compose Release Assurance must start, inspect, restart, and validate Docker Compose services during a rehearsal.

A common approach is to run the orchestration tool inside a container and mount the Docker socket:

```text

/var/run/docker.sock

```

Docker socket access is highly privileged. A container that can control the Docker daemon can often gain broad control over the host environment.

The project is intended to demonstrate secure and understandable engineering practices. The orchestration model must therefore minimize unnecessary privilege escalation.

## Decision

`rehearsalctl` will run directly on an authorized developer workstation, controlled CI runner, or approved automation host.

It will invoke Docker and Docker Compose through a controlled host-side interface.

Application containers must not receive Docker socket access.

## Consequences

### Positive

* Avoids giving application containers Docker-daemon control.

* Keeps the trust boundary explicit.

* Matches common CI runner and automation-host patterns.

* Simplifies local debugging and evidence collection.

* Supports secure future integration with Azure Pipelines, Jenkins, and Ansible.

### Negative

* The host or CI runner requires Docker and Docker Compose access.

* The CLI must validate command execution carefully.

* Cross-platform behavior must be documented and tested.

* The orchestration layer needs clear timeout, retry, and error-handling behavior.

## Alternatives Considered

### Containerized orchestrator with Docker socket mount

Rejected for MVP.

Reason: Docker socket access introduces high privilege and is not necessary for the first implementation.

### Docker-in-Docker

Rejected for MVP.

Reason: Adds operational complexity, storage overhead, networking complexity, and security concerns without solving a required MVP problem.

### Kubernetes controller

Rejected for MVP.

Reason: The project target is Docker Compose-based release rehearsal. Kubernetes would expand the scope beyond the current product boundary.

## Security Impact

* Docker control remains limited to explicitly authorized hosts or runners.

* Application services do not gain host-level orchestration capability.

* Future CI integrations must use least-privilege service identities and protected secrets.

## Operational Impact

* Prerequisites must document Docker Engine and Docker Compose requirements.

* CI templates must run on an agent with authorized Docker access.

* Diagnostics collection runs from the same trusted execution context.

## Rollback Plan

No runtime deployment rollback is required for this ADR.

The architectural decision may be revisited only if a future orchestration container can be designed with a safer, narrowly scoped control interface and a documented security review.
