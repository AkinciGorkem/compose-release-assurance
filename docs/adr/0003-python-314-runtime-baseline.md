# ADR-0003: Use Python 3.14 as the Initial Supported Runtime

**Status:** Accepted

**Date:** 2026-06-25

## Context

ADR-0002 established Python as the primary implementation language and initially recorded Python 3.12 as the baseline runtime.

Before implementation began, the local development environment was verified. Python 3.14.3 is installed and available, while Python 3.12 is not installed.

The project must avoid claiming compatibility that has not been tested. The runtime policy must therefore reflect the actual supported development environment and remain simple for contributors.

## Decision

Python 3.14 is the initial supported runtime for:

* Local development

* Automated tests

* CI validation

* The reference application container

* The `rehearsalctl` CLI

The project will initially declare Python 3.14 as its only supported runtime.

Additional Python versions may be added only after automated CI validation confirms compatibility and the technology documentation is updated.

ADR-0002 remains valid for the Python-first language-boundary decision. This ADR supersedes only its Python minor-version baseline.

## Consequences

### Positive

* Uses an installed and current local runtime.

* Avoids unnecessary installation and environment complexity.

* Keeps the first quality-gate setup reproducible.

* Prevents unsupported-version claims.

* Keeps Docker, CI, local development, and documentation aligned.

### Negative

* Contributors using earlier Python versions must install Python 3.14 initially.

* Broader version compatibility is deferred until CI proves it.

* Dependency selection must be verified against Python 3.14.

## Alternatives Considered

### Keep Python 3.12 as the initial baseline

Rejected.

Python 3.12 is not installed in the verified local environment. Installing and maintaining a second runtime before any code exists adds complexity without a demonstrated need.

### Support Python 3.12, 3.13, and 3.14 immediately

Rejected.

The project must not claim a compatibility matrix before dependencies, quality tooling, containers, and tests have been executed against each version.

### Use Python 3.14 locally but Python 3.12 in containers

Rejected.

Different local and container runtimes would introduce avoidable environment drift during the MVP.

## Security Impact

* A single verified runtime reduces dependency and supply-chain variation.

* Container and CI images can use the same runtime family.

* Future version expansion requires explicit testing and review.

## Operational Impact

* Contributors need Python 3.14 for the initial development workflow.

* CI will initially validate Python 3.14 only.

* Docker images will use a Python 3.14 base image until a future ADR changes the policy.

## Rollback Plan

The project can move to another supported Python version through a documented ADR, dependency validation, CI test evidence, and a controlled migration plan.
