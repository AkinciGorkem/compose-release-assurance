# ADR-0004: Adopt a Source-Available No-Sale License Policy

**Status:** Accepted
**Date:** 2026-06-25

## Context

Compose Release Assurance is intended to be publicly available so that individuals and organizations can inspect, learn from, use, and contribute to the project.

The project owner does not want third parties to take the Software, make minimal changes, and sell the Software or a substantially equivalent offering as their own commercial product.

The repository initially used the Apache License, Version 2.0. Apache-2.0 permits commercial redistribution and sale, which does not satisfy the project’s intended no-sale condition.

## Decision

The project will use the Apache License, Version 2.0, with the Commons Clause License Condition v1.0.

The project will be described as:

```text
Public and source-available under a no-sale condition.
```

The project must not be described as OSI-approved open-source software.

A `NOTICE` file and `docs/LICENSE_POLICY.md` will document project origin, attribution, and the intended license interpretation.

## Consequences

### Positive

* Source remains publicly visible and usable under documented terms.
* The project owner retains the ability to grant separate written commercial permissions.
* The license discourages resale and substantially equivalent paid offerings.
* License terms and authorship are visible to users and contributors.
* The project remains accessible for learning, evaluation, engineering use, and contribution.

### Negative

* The project cannot accurately be described as OSI-approved open-source software.
* Some organizations may avoid source-available licensing restrictions.
* Commercial-use interpretation can depend on the factual use case and jurisdiction.
* The condition does not technically prevent misuse; it establishes legal restrictions.
* Existing versions previously published under Apache-2.0 retain their original license grants.

## Alternatives Considered

### Keep Apache License 2.0

Rejected.

Apache-2.0 permits commercial redistribution and sale.

### GPL or AGPL

Rejected.

These licenses impose copyleft obligations but still allow commercial sale and redistribution.

### Noncommercial-only license

Rejected.

A broad noncommercial restriction could prevent legitimate internal organizational use, which conflicts with the project goal of allowing free use and learning.

### Custom license

Rejected.

A custom license would create ambiguity, increase legal risk, and make adoption harder.

## Security Impact

* No direct runtime-security impact.
* Contributors must not submit code, assets, or configuration they do not have permission to license.
* License notices and project attribution must be retained.

## Operational Impact

* Repository documentation must use source-available terminology.
* Public release documentation must clearly state the no-sale condition.
* Commercial exception requests require written approval from the copyright holder.

## Rollback Plan

The copyright holder may change the license policy for future versions through a new documented decision.

License grants already made for previously published versions cannot be retroactively withdrawn.
