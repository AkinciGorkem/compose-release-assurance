# ADR-0005: PostgreSQL Relational Ledger Persistence Baseline

**Status:** Accepted

**Date:** 2026-07-03

## Context

The reference ledger must persist synthetic transfers, idempotency records, debit and
credit entries, and audit records without coupling domain rules to a database driver,
HTTP framework, Docker Compose, or release orchestration.

The project requires one idempotency key to map to one transfer, balanced double-entry
records, an audit record for every accepted transfer, explicit failure behavior, and
evidence-based integrity validation. The in-memory `LedgerBook` remains test-only and
single-process; it cannot provide the transaction isolation or durable constraints
required by the future Compose-based reference stack.

## Decision

The persistence target is PostgreSQL. The first persistence asset is a versioned,
plain-SQL migration under `infra/postgres/migrations/`.

The initial migration uses normalized tables for:

- `transfers`
- `idempotency_records`
- `ledger_entries`
- `audit_records`

It enforces local relational invariants through primary keys, foreign keys, unique
constraints, non-empty identifiers, positive numeric amounts, uppercase three-letter
currencies, distinct transfer accounts, one ledger-entry direction per transfer, and
one audit and idempotency record per transfer.

Identifiers remain `TEXT` in the first schema to match the existing domain contract
without prematurely making UUID formatting a domain requirement. The future PostgreSQL
adapter must execute all writes within one transaction and must preserve the existing
idempotency conflict and safe-replay semantics.

The initial schema does not use triggers for cross-row debit/credit balance validation.
The application adapter will create all records atomically, and the existing integrity
validator plus future rehearsal checks remain mandatory controls.

## Alternatives Considered

### Start with an ORM-managed schema

Rejected for the baseline. A plain SQL migration makes the database constraints,
indexes, and transaction-relevant structure directly reviewable. An ORM can be
considered later only when it demonstrably reduces rather than obscures complexity.

### Keep the in-memory ledger as the reference persistence model

Rejected. It is explicitly test-only, single-process, and cannot provide durable state,
database constraints, or concurrent idempotency guarantees.

### Add database triggers now

Deferred. Constraint triggers can enforce additional cross-row invariants, but they add
significant complexity before a real adapter and integration environment exist. The
first live integration slice must verify the current database constraints and
transactional write behavior.

## Consequences

### Positive

- Persistent-storage rules are explicit, versioned, and independently reviewable.
- The schema matches the domain's synthetic ledger entities without importing database
  concerns into domain code.
- The design creates a clear path to transaction-backed idempotency and Compose-based
  integration testing.
- The migration contains no credentials, customer data, internal endpoints, or vendor
  coupling.

### Negative

- The SQL asset is not yet proof of a live PostgreSQL deployment; it requires the next
  integration slice to execute it in a real database.
- Cross-row balance validation remains an application and rehearsal responsibility
  until a justified database-level constraint is added.
- A future adapter must carefully map database constraint failures to explicit
  application errors.

## Security Impact

The migration contains schema only. It must not contain database passwords, connection
URLs, real account identifiers, customer data, or internal infrastructure details.
Future Compose configuration keeps PostgreSQL on an internal network by default.

## Operational Impact

The next persistence slice must execute this migration against a real PostgreSQL
container and test both success and constraint-failure paths. A successful static
contract test does not authorize a production deployment or a release decision.

## Rollback Plan

For an ephemeral local development database, the schema can be removed by recreating
the disposable database volume. For any persistent environment, do not apply a
destructive rollback automatically; use an approved forward migration or restore from
a verified backup according to the environment's change process.
