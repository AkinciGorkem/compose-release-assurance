"""Application-facing persistence boundary for accepted transfer state."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ledger_api.models import LedgerSnapshot, TransferRequest, TransferResult


@runtime_checkable
class LedgerStore(Protocol):
    """Atomic persistence boundary for accepted synthetic transfers.

    An implementation must either create one transfer, two balanced ledger entries,
    one audit record, and one idempotency record together, or return the original
    result for a safe replay. It must not leave partial state behind when it fails.
    """

    def submit(self, request: TransferRequest) -> TransferResult:
        """Create or safely replay a transfer as one atomic operation."""

        ...

    def snapshot(self) -> LedgerSnapshot:
        """Return one internally consistent read of accepted transfer state."""

        ...
