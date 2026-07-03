from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from itertools import count

from ledger_api import (
    LedgerApplicationService,
    LedgerBook,
    LedgerSnapshot,
    LedgerStore,
    TransferRequest,
    TransferResult,
)


def test_application_service_submits_and_replays_without_duplicate_state() -> None:
    ledger = _ledger()
    service = LedgerApplicationService(ledger)
    request = _request()

    initial = service.submit_transfer(request)
    replay = service.submit_transfer(request)
    snapshot = ledger.snapshot()

    assert initial.replayed is False
    assert replay.replayed is True
    assert replay.transfer.id == initial.transfer.id
    assert len(snapshot.transfers) == 1
    assert len(snapshot.ledger_entries) == 2
    assert len(snapshot.audit_records) == 1
    assert len(snapshot.idempotency_records) == 1


def test_application_service_uses_only_the_ledger_store_contract() -> None:
    recording_store = _RecordingLedgerStore(_ledger())
    service = LedgerApplicationService(recording_store)

    service.submit_transfer(_request())

    assert recording_store.submit_calls == 1
    assert recording_store.snapshot_calls == 0

    report = service.validate_integrity()

    assert report.is_valid is True
    assert recording_store.snapshot_calls == 1


def test_application_service_returns_integrity_failures_from_the_store_snapshot() -> None:
    ledger = _ledger()
    ledger.submit(_request())
    valid_snapshot = ledger.snapshot()
    corrupted_snapshot = LedgerSnapshot(
        transfers=valid_snapshot.transfers,
        ledger_entries=(
            valid_snapshot.ledger_entries[0],
            replace(valid_snapshot.ledger_entries[1], amount=Decimal("24.99")),
        ),
        audit_records=valid_snapshot.audit_records,
        idempotency_records=valid_snapshot.idempotency_records,
    )
    service = LedgerApplicationService(_StaticSnapshotLedgerStore(corrupted_snapshot))

    report = service.validate_integrity()

    violation_codes = {violation.code for violation in report.violations}
    assert report.is_valid is False
    assert "ledger_entry_mismatch" in violation_codes
    assert "ledger_amount_mismatch" in violation_codes


def test_ledger_book_satisfies_the_ledger_store_contract() -> None:
    assert isinstance(_ledger(), LedgerStore)


class _RecordingLedgerStore:
    def __init__(self, delegate: LedgerBook) -> None:
        self._delegate = delegate
        self.submit_calls = 0
        self.snapshot_calls = 0

    def submit(self, request: TransferRequest) -> TransferResult:
        self.submit_calls += 1
        return self._delegate.submit(request)

    def snapshot(self) -> LedgerSnapshot:
        self.snapshot_calls += 1
        return self._delegate.snapshot()


class _StaticSnapshotLedgerStore:
    def __init__(self, snapshot_value: LedgerSnapshot) -> None:
        self._snapshot_value = snapshot_value

    def submit(self, request: TransferRequest) -> TransferResult:
        raise AssertionError("submit is not expected during integrity validation.")

    def snapshot(self) -> LedgerSnapshot:
        return self._snapshot_value


def _request() -> TransferRequest:
    return TransferRequest(
        idempotency_key="retry-application-001",
        debit_account_id="account-debit",
        credit_account_id="account-credit",
        amount=Decimal("25.00"),
        currency="USD",
        correlation_id="application-service-test",
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
