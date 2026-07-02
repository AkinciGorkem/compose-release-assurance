"""Single-process in-memory implementation of the synthetic ledger workflow."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from ledger_api.errors import DomainValidationError, IdempotencyConflictError
from ledger_api.models import (
    AuditRecord,
    EntryDirection,
    IdempotencyRecord,
    LedgerEntry,
    LedgerSnapshot,
    Transfer,
    TransferRequest,
    TransferResult,
)

Clock = Callable[[], datetime]
IdentifierFactory = Callable[[], str]


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _new_identifier() -> str:
    return str(uuid4())


def _require_utc(timestamp: object) -> datetime:
    if not isinstance(timestamp, datetime):
        raise DomainValidationError("clock must return a datetime value.")

    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise DomainValidationError("clock must return a timezone-aware datetime.")

    return timestamp.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class _AcceptedTransfer:
    """Internal immutable record used by the test-only in-memory ledger."""

    transfer: Transfer
    debit_entry: LedgerEntry
    credit_entry: LedgerEntry
    audit_record: AuditRecord
    idempotency_record: IdempotencyRecord


class LedgerBook:
    """Test-oriented in-memory ledger with explicit idempotency semantics.

    This class is intentionally single-process and is not the future PostgreSQL
    concurrency implementation. Database constraints and transaction isolation
    will be added in the persistence phase.
    """

    def __init__(
        self,
        *,
        clock: Clock = _utc_now,
        identifier_factory: IdentifierFactory = _new_identifier,
    ) -> None:
        self._clock = clock
        self._identifier_factory = identifier_factory
        self._accepted_by_idempotency_key: dict[str, _AcceptedTransfer] = {}
        self._issued_identifiers: set[str] = set()

    def submit(self, request: TransferRequest) -> TransferResult:
        """Accept a request once or return the original result for a safe replay."""

        existing = self._accepted_by_idempotency_key.get(request.idempotency_key)
        if existing is not None:
            if existing.transfer.request_fingerprint != request.fingerprint:
                raise IdempotencyConflictError(
                    "idempotency_key was already used for a different transfer request."
                )
            return _result_from(existing, replayed=True)

        timestamp = _require_utc(self._clock())
        transfer_id, debit_entry_id, credit_entry_id, audit_record_id = (
            self._next_unique_identifiers()
        )
        transfer = Transfer(
            id=transfer_id,
            idempotency_key=request.idempotency_key,
            request_fingerprint=request.fingerprint,
            debit_account_id=request.debit_account_id,
            credit_account_id=request.credit_account_id,
            amount=request.amount,
            currency=request.currency,
            created_at=timestamp,
        )
        debit_entry = LedgerEntry(
            id=debit_entry_id,
            transfer_id=transfer.id,
            direction=EntryDirection.DEBIT,
            account_id=transfer.debit_account_id,
            amount=transfer.amount,
            currency=transfer.currency,
            created_at=timestamp,
        )
        credit_entry = LedgerEntry(
            id=credit_entry_id,
            transfer_id=transfer.id,
            direction=EntryDirection.CREDIT,
            account_id=transfer.credit_account_id,
            amount=transfer.amount,
            currency=transfer.currency,
            created_at=timestamp,
        )
        audit_record = AuditRecord(
            id=audit_record_id,
            transfer_id=transfer.id,
            event_type="TRANSFER_ACCEPTED",
            correlation_id=request.correlation_id,
            occurred_at=timestamp,
        )
        idempotency_record = IdempotencyRecord(
            key=request.idempotency_key,
            request_fingerprint=request.fingerprint,
            transfer_id=transfer.id,
            created_at=timestamp,
        )
        accepted = _AcceptedTransfer(
            transfer=transfer,
            debit_entry=debit_entry,
            credit_entry=credit_entry,
            audit_record=audit_record,
            idempotency_record=idempotency_record,
        )

        self._accepted_by_idempotency_key[request.idempotency_key] = accepted
        return _result_from(accepted, replayed=False)

    def snapshot(self) -> LedgerSnapshot:
        """Return the current synthetic state without exposing mutable storage."""

        accepted_transfers = tuple(self._accepted_by_idempotency_key.values())
        return LedgerSnapshot(
            transfers=tuple(item.transfer for item in accepted_transfers),
            ledger_entries=tuple(
                entry
                for item in accepted_transfers
                for entry in (item.debit_entry, item.credit_entry)
            ),
            audit_records=tuple(item.audit_record for item in accepted_transfers),
            idempotency_records=tuple(item.idempotency_record for item in accepted_transfers),
        )

    def _next_identifier(self) -> str:
        identifier = self._identifier_factory()
        if not isinstance(identifier, str) or not identifier.strip():
            raise DomainValidationError("identifier_factory must return a non-empty string.")

        return identifier.strip()

    def _next_unique_identifiers(self) -> tuple[str, str, str, str]:
        transfer_id = self._next_identifier()
        debit_entry_id = self._next_identifier()
        credit_entry_id = self._next_identifier()
        audit_record_id = self._next_identifier()
        candidate_identifiers = (
            transfer_id,
            debit_entry_id,
            credit_entry_id,
            audit_record_id,
        )

        if len(set(candidate_identifiers)) != len(candidate_identifiers):
            raise DomainValidationError(
                "identifier_factory must return unique identifiers for each transfer."
            )

        if any(identifier in self._issued_identifiers for identifier in candidate_identifiers):
            raise DomainValidationError(
                "identifier_factory returned an identifier already used by the ledger."
            )

        self._issued_identifiers.update(candidate_identifiers)
        return candidate_identifiers


def _result_from(accepted: _AcceptedTransfer, *, replayed: bool) -> TransferResult:
    return TransferResult(
        transfer=accepted.transfer,
        ledger_entries=(accepted.debit_entry, accepted.credit_entry),
        audit_record=accepted.audit_record,
        replayed=replayed,
    )
