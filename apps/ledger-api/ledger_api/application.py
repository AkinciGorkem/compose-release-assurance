"""Application service for transfer submission and integrity assessment."""

from __future__ import annotations

from ledger_api.integrity import IntegrityReport, validate_ledger_snapshot
from ledger_api.models import TransferRequest, TransferResult
from ledger_api.ports import LedgerStore


class LedgerApplicationService:
    """Coordinate transfer use cases without owning domain or persistence rules.

    Outer adapters such as HTTP or a rehearsal CLI use this service. The supplied
    store owns atomic write behavior; the domain owns transfer invariants.
    """

    def __init__(self, ledger_store: LedgerStore) -> None:
        self._ledger_store = ledger_store

    def submit_transfer(self, request: TransferRequest) -> TransferResult:
        """Submit a validated transfer request through the atomic store boundary."""

        return self._ledger_store.submit(request)

    def validate_integrity(self) -> IntegrityReport:
        """Validate an internally consistent snapshot from the configured store."""

        return validate_ledger_snapshot(self._ledger_store.snapshot())
