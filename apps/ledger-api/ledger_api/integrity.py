"""Integrity validation for synthetic ledger snapshots."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from ledger_api.models import (
    AuditRecord,
    EntryDirection,
    IdempotencyRecord,
    LedgerEntry,
    LedgerSnapshot,
    Transfer,
)


@dataclass(frozen=True, slots=True)
class IntegrityViolation:
    """One explicit invariant failure found in a ledger snapshot."""

    code: str
    message: str


@dataclass(frozen=True, slots=True)
class IntegrityReport:
    """Result of validating a synthetic ledger snapshot."""

    violations: tuple[IntegrityViolation, ...]

    @property
    def is_valid(self) -> bool:
        return not self.violations


def validate_ledger_snapshot(snapshot: LedgerSnapshot) -> IntegrityReport:
    """Validate transfer, idempotency, ledger-entry, and audit invariants."""

    violations: list[IntegrityViolation] = []
    _validate_unique_identifiers(
        (transfer.id for transfer in snapshot.transfers),
        code="duplicate_transfer_id",
        message="A transfer identifier appears more than once.",
        violations=violations,
    )
    _validate_unique_identifiers(
        (entry.id for entry in snapshot.ledger_entries),
        code="duplicate_ledger_entry_id",
        message="A ledger entry identifier appears more than once.",
        violations=violations,
    )
    _validate_unique_identifiers(
        (audit.id for audit in snapshot.audit_records),
        code="duplicate_audit_record_id",
        message="An audit record identifier appears more than once.",
        violations=violations,
    )
    _validate_unique_identifiers(
        (record.key for record in snapshot.idempotency_records),
        code="duplicate_idempotency_key",
        message="An idempotency key appears more than once.",
        violations=violations,
    )

    transfers_by_id = _index_transfers(snapshot.transfers)
    entries_by_transfer_id = _group_entries(snapshot.ledger_entries)
    audits_by_transfer_id = _group_audits(snapshot.audit_records)
    idempotency_records_by_key = _group_idempotency_records(snapshot.idempotency_records)

    _validate_orphan_entries(snapshot.ledger_entries, transfers_by_id, violations)
    _validate_orphan_audits(snapshot.audit_records, transfers_by_id, violations)
    _validate_orphan_idempotency_records(
        snapshot.idempotency_records,
        transfers_by_id,
        violations,
    )

    for transfer in snapshot.transfers:
        _validate_transfer_entries(
            transfer,
            entries_by_transfer_id.get(transfer.id, ()),
            violations,
        )
        _validate_transfer_audits(
            audits_by_transfer_id.get(transfer.id, ()),
            violations,
        )
        _validate_transfer_idempotency(
            transfer,
            idempotency_records_by_key.get(transfer.idempotency_key, ()),
            violations,
        )

    return IntegrityReport(violations=tuple(violations))


def _validate_unique_identifiers(
    identifiers: Iterable[str],
    *,
    code: str,
    message: str,
    violations: list[IntegrityViolation],
) -> None:
    for count in Counter(identifiers).values():
        if count > 1:
            violations.append(IntegrityViolation(code=code, message=message))


def _index_transfers(transfers: tuple[Transfer, ...]) -> dict[str, Transfer]:
    return {transfer.id: transfer for transfer in transfers}


def _group_entries(
    entries: tuple[LedgerEntry, ...],
) -> dict[str, tuple[LedgerEntry, ...]]:
    grouped: defaultdict[str, list[LedgerEntry]] = defaultdict(list)
    for entry in entries:
        grouped[entry.transfer_id].append(entry)

    return {transfer_id: tuple(items) for transfer_id, items in grouped.items()}


def _group_audits(
    audits: tuple[AuditRecord, ...],
) -> dict[str, tuple[AuditRecord, ...]]:
    grouped: defaultdict[str, list[AuditRecord]] = defaultdict(list)
    for audit in audits:
        grouped[audit.transfer_id].append(audit)

    return {transfer_id: tuple(items) for transfer_id, items in grouped.items()}


def _group_idempotency_records(
    records: tuple[IdempotencyRecord, ...],
) -> dict[str, tuple[IdempotencyRecord, ...]]:
    grouped: defaultdict[str, list[IdempotencyRecord]] = defaultdict(list)
    for record in records:
        grouped[record.key].append(record)

    return {key: tuple(items) for key, items in grouped.items()}


def _validate_orphan_entries(
    entries: tuple[LedgerEntry, ...],
    transfers_by_id: dict[str, Transfer],
    violations: list[IntegrityViolation],
) -> None:
    for entry in entries:
        if entry.transfer_id not in transfers_by_id:
            violations.append(
                IntegrityViolation(
                    code="ledger_entry_references_unknown_transfer",
                    message="A ledger entry references an unknown transfer.",
                )
            )


def _validate_orphan_audits(
    audits: tuple[AuditRecord, ...],
    transfers_by_id: dict[str, Transfer],
    violations: list[IntegrityViolation],
) -> None:
    for audit in audits:
        if audit.transfer_id not in transfers_by_id:
            violations.append(
                IntegrityViolation(
                    code="audit_record_references_unknown_transfer",
                    message="An audit record references an unknown transfer.",
                )
            )


def _validate_orphan_idempotency_records(
    records: tuple[IdempotencyRecord, ...],
    transfers_by_id: dict[str, Transfer],
    violations: list[IntegrityViolation],
) -> None:
    for record in records:
        if record.transfer_id not in transfers_by_id:
            violations.append(
                IntegrityViolation(
                    code="idempotency_references_unknown_transfer",
                    message="An idempotency record references an unknown transfer.",
                )
            )


def _validate_transfer_entries(
    transfer: Transfer,
    entries: tuple[LedgerEntry, ...],
    violations: list[IntegrityViolation],
) -> None:
    if len(entries) != 2:
        violations.append(
            IntegrityViolation(
                code="invalid_ledger_entry_count",
                message="Each transfer must have exactly two ledger entries.",
            )
        )
        return

    debit_entries = [entry for entry in entries if entry.direction is EntryDirection.DEBIT]
    credit_entries = [entry for entry in entries if entry.direction is EntryDirection.CREDIT]
    if len(debit_entries) != 1 or len(credit_entries) != 1:
        violations.append(
            IntegrityViolation(
                code="invalid_ledger_directions",
                message="Each transfer must have exactly one debit and one credit entry.",
            )
        )
        return

    debit_entry = debit_entries[0]
    credit_entry = credit_entries[0]
    if not _entries_match_transfer(transfer, debit_entry, credit_entry):
        violations.append(
            IntegrityViolation(
                code="ledger_entry_mismatch",
                message="Ledger entries must match the transfer accounts, amount, and currency.",
            )
        )

    if debit_entry.amount != credit_entry.amount:
        violations.append(
            IntegrityViolation(
                code="ledger_amount_mismatch",
                message="Debit and credit amounts must be equal.",
            )
        )


def _entries_match_transfer(
    transfer: Transfer,
    debit_entry: LedgerEntry,
    credit_entry: LedgerEntry,
) -> bool:
    return (
        debit_entry.account_id == transfer.debit_account_id
        and credit_entry.account_id == transfer.credit_account_id
        and debit_entry.amount == transfer.amount
        and credit_entry.amount == transfer.amount
        and debit_entry.currency == transfer.currency
        and credit_entry.currency == transfer.currency
    )


def _validate_transfer_audits(
    audits: tuple[AuditRecord, ...],
    violations: list[IntegrityViolation],
) -> None:
    if len(audits) != 1:
        violations.append(
            IntegrityViolation(
                code="invalid_audit_record_count",
                message="Each transfer must have exactly one audit record.",
            )
        )
        return

    if audits[0].event_type != "TRANSFER_ACCEPTED":
        violations.append(
            IntegrityViolation(
                code="invalid_audit_event_type",
                message="The audit record must describe an accepted transfer.",
            )
        )


def _validate_transfer_idempotency(
    transfer: Transfer,
    records: tuple[IdempotencyRecord, ...],
    violations: list[IntegrityViolation],
) -> None:
    if len(records) != 1:
        violations.append(
            IntegrityViolation(
                code="invalid_idempotency_record_count",
                message="Each transfer must have exactly one idempotency record.",
            )
        )
        return

    record = records[0]
    if (
        record.transfer_id != transfer.id
        or record.request_fingerprint != transfer.request_fingerprint
    ):
        violations.append(
            IntegrityViolation(
                code="idempotency_record_mismatch",
                message="The idempotency record must match its transfer and request fingerprint.",
            )
        )
