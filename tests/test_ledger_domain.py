from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from itertools import count
from typing import cast

import pytest
from ledger_api import (
    DomainValidationError,
    IdempotencyConflictError,
    LedgerBook,
    LedgerSnapshot,
    TransferRequest,
    validate_ledger_snapshot,
)


def test_valid_transfer_creates_balanced_records_and_audit_record() -> None:
    ledger = _ledger()
    result = ledger.submit(_request())

    snapshot = ledger.snapshot()
    report = validate_ledger_snapshot(snapshot)

    assert result.replayed is False
    assert len(snapshot.transfers) == 1
    assert len(snapshot.ledger_entries) == 2
    assert len(snapshot.audit_records) == 1
    assert len(snapshot.idempotency_records) == 1
    assert report.is_valid is True
    assert report.violations == ()


def test_identical_retry_returns_original_transfer_without_duplicate_records() -> None:
    ledger = _ledger()
    request = _request()

    initial = ledger.submit(request)
    replay = ledger.submit(request)
    snapshot = ledger.snapshot()

    assert replay.replayed is True
    assert replay.transfer.id == initial.transfer.id
    assert replay.ledger_entries == initial.ledger_entries
    assert replay.audit_record == initial.audit_record
    assert len(snapshot.transfers) == 1
    assert len(snapshot.ledger_entries) == 2
    assert len(snapshot.audit_records) == 1
    assert len(snapshot.idempotency_records) == 1


def test_retry_with_changed_correlation_id_is_a_safe_replay() -> None:
    ledger = _ledger()
    initial_request = _request(correlation_id="initial-attempt")
    replay_request = _request(correlation_id="retry-attempt")

    initial = ledger.submit(initial_request)
    replay = ledger.submit(replay_request)

    assert replay.replayed is True
    assert replay.transfer.id == initial.transfer.id
    assert replay.audit_record.correlation_id == "initial-attempt"
    assert _snapshot_counts(ledger.snapshot()) == (1, 2, 1, 1)


def test_reused_idempotency_key_with_changed_payload_raises_conflict() -> None:
    ledger = _ledger()
    initial = _request()
    changed = _request(amount=Decimal("26.00"))

    ledger.submit(initial)

    with pytest.raises(IdempotencyConflictError):
        ledger.submit(changed)

    assert _snapshot_counts(ledger.snapshot()) == (1, 2, 1, 1)


@pytest.mark.parametrize("amount", (Decimal("0"), Decimal("-0.01")))
def test_non_positive_amount_is_rejected_without_state_change(amount: Decimal) -> None:
    ledger = _ledger()

    with pytest.raises(DomainValidationError):
        _request(amount=amount)

    assert _is_empty(ledger.snapshot())


def test_amount_with_more_than_two_decimal_places_is_rejected_without_state_change() -> None:
    ledger = _ledger()

    with pytest.raises(DomainValidationError):
        _request(amount=Decimal("25.001"))

    assert _is_empty(ledger.snapshot())


def test_empty_idempotency_key_is_rejected_without_state_change() -> None:
    ledger = _ledger()

    with pytest.raises(DomainValidationError):
        _request(idempotency_key="   ")

    assert _is_empty(ledger.snapshot())


def test_matching_accounts_are_rejected_without_state_change() -> None:
    ledger = _ledger()

    with pytest.raises(DomainValidationError):
        _request(debit_account_id="account-same", credit_account_id="account-same")

    assert _is_empty(ledger.snapshot())


@pytest.mark.parametrize("currency", ("usd", "US", "USDD", "ÜSD"))
def test_invalid_currency_is_rejected_without_state_change(currency: str) -> None:
    ledger = _ledger()

    with pytest.raises(DomainValidationError):
        _request(currency=currency)

    assert _is_empty(ledger.snapshot())


def test_binary_float_amount_is_rejected() -> None:
    with pytest.raises(DomainValidationError):
        _request(amount=cast(Decimal, 25.0))


def test_duplicate_identifiers_within_one_transfer_are_rejected_without_state_change() -> None:
    ledger = LedgerBook(clock=_fixed_clock, identifier_factory=lambda: "duplicate-id")

    with pytest.raises(DomainValidationError, match="unique identifiers"):
        ledger.submit(_request())

    assert _is_empty(ledger.snapshot())


def test_reused_identifier_from_factory_is_rejected_without_state_change() -> None:
    identifiers = iter(
        (
            "id-1",
            "id-2",
            "id-3",
            "id-4",
            "id-1",
            "id-6",
            "id-7",
            "id-8",
        )
    )
    ledger = LedgerBook(clock=_fixed_clock, identifier_factory=lambda: next(identifiers))

    ledger.submit(_request(idempotency_key="retry-001"))

    with pytest.raises(DomainValidationError, match="already used"):
        ledger.submit(_request(idempotency_key="retry-002"))

    assert _snapshot_counts(ledger.snapshot()) == (1, 2, 1, 1)


def test_invalid_clock_output_is_rejected_without_state_change() -> None:
    ledger = LedgerBook(
        clock=cast(Callable[[], datetime], lambda: "not-a-datetime"),
        identifier_factory=_identifier_factory(),
    )

    with pytest.raises(DomainValidationError, match="clock must return a datetime value"):
        ledger.submit(_request())

    assert _is_empty(ledger.snapshot())


def test_request_fingerprint_is_unambiguous_for_control_characters() -> None:
    first = _request(
        debit_account_id="account-a\x1faccount-b",
        credit_account_id="account-c",
    )
    second = _request(
        debit_account_id="account-a",
        credit_account_id="account-b\x1faccount-c",
    )

    assert first.fingerprint != second.fingerprint


def test_integrity_validator_detects_unbalanced_and_duplicate_idempotency_records() -> None:
    ledger = _ledger()
    ledger.submit(_request())
    snapshot = ledger.snapshot()

    credit_entry = snapshot.ledger_entries[1]
    unbalanced_snapshot = LedgerSnapshot(
        transfers=snapshot.transfers,
        ledger_entries=(
            snapshot.ledger_entries[0],
            replace(credit_entry, amount=Decimal("24.99")),
        ),
        audit_records=snapshot.audit_records,
        idempotency_records=snapshot.idempotency_records,
    )
    duplicate_snapshot = LedgerSnapshot(
        transfers=snapshot.transfers,
        ledger_entries=snapshot.ledger_entries,
        audit_records=snapshot.audit_records,
        idempotency_records=(
            snapshot.idempotency_records[0],
            snapshot.idempotency_records[0],
        ),
    )

    unbalanced_codes = {
        violation.code for violation in validate_ledger_snapshot(unbalanced_snapshot).violations
    }
    duplicate_codes = {
        violation.code for violation in validate_ledger_snapshot(duplicate_snapshot).violations
    }

    assert "ledger_entry_mismatch" in unbalanced_codes
    assert "ledger_amount_mismatch" in unbalanced_codes
    assert "duplicate_idempotency_key" in duplicate_codes
    assert "invalid_idempotency_record_count" in duplicate_codes


def test_integrity_validator_detects_duplicate_entity_ids_and_orphan_records() -> None:
    ledger = _ledger()
    ledger.submit(_request(idempotency_key="retry-001"))
    ledger.submit(_request(idempotency_key="retry-002"))
    snapshot = ledger.snapshot()

    duplicate_entry = replace(
        snapshot.ledger_entries[2],
        id=snapshot.ledger_entries[0].id,
    )
    duplicate_audit = replace(
        snapshot.audit_records[1],
        id=snapshot.audit_records[0].id,
    )
    orphan_entry = replace(
        snapshot.ledger_entries[0],
        id="orphan-entry",
        transfer_id="missing-transfer",
    )
    orphan_audit = replace(
        snapshot.audit_records[0],
        id="orphan-audit",
        transfer_id="missing-transfer",
    )
    orphan_idempotency_record = replace(
        snapshot.idempotency_records[0],
        transfer_id="missing-transfer",
    )
    corrupted_snapshot = LedgerSnapshot(
        transfers=snapshot.transfers,
        ledger_entries=(
            snapshot.ledger_entries[0],
            snapshot.ledger_entries[1],
            duplicate_entry,
            snapshot.ledger_entries[3],
            orphan_entry,
        ),
        audit_records=(
            snapshot.audit_records[0],
            duplicate_audit,
            orphan_audit,
        ),
        idempotency_records=(
            orphan_idempotency_record,
            snapshot.idempotency_records[1],
        ),
    )

    codes = {
        violation.code for violation in validate_ledger_snapshot(corrupted_snapshot).violations
    }

    assert "duplicate_ledger_entry_id" in codes
    assert "duplicate_audit_record_id" in codes
    assert "ledger_entry_references_unknown_transfer" in codes
    assert "audit_record_references_unknown_transfer" in codes
    assert "idempotency_references_unknown_transfer" in codes


def _request(
    *,
    idempotency_key: str = "retry-001",
    debit_account_id: str = "account-debit",
    credit_account_id: str = "account-credit",
    amount: Decimal = Decimal("25.00"),
    currency: str = "USD",
    correlation_id: str | None = "scenario-api-restart",
) -> TransferRequest:
    return TransferRequest(
        idempotency_key=idempotency_key,
        debit_account_id=debit_account_id,
        credit_account_id=credit_account_id,
        amount=amount,
        currency=currency,
        correlation_id=correlation_id,
    )


def _ledger() -> LedgerBook:
    return LedgerBook(clock=_fixed_clock, identifier_factory=_identifier_factory())


def _fixed_clock() -> datetime:
    return datetime(2026, 7, 2, 9, 30, tzinfo=UTC)


def _identifier_factory() -> Callable[[], str]:
    sequence = count(1)

    def next_identifier() -> str:
        return f"id-{next(sequence)}"

    return next_identifier


def _snapshot_counts(snapshot: LedgerSnapshot) -> tuple[int, int, int, int]:
    return (
        len(snapshot.transfers),
        len(snapshot.ledger_entries),
        len(snapshot.audit_records),
        len(snapshot.idempotency_records),
    )


def _is_empty(snapshot: LedgerSnapshot) -> bool:
    return _snapshot_counts(snapshot) == (0, 0, 0, 0)
