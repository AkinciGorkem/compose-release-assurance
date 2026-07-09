"""PostgreSQL persistence adapter for the synthetic ledger store."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from psycopg import Connection

from ledger_api.models import LedgerSnapshot, TransferRequest, TransferResult

ConnectionFactory = Callable[[], Connection[Any]]


class PostgresLedgerStore:
    """PostgreSQL-backed implementation of the LedgerStore port.

    The caller owns configuration and secret loading. This adapter receives a
    connection factory so credentials do not need to live in module-level state,
    environment globals, logs, or committed files.
    """

    def __init__(self, connection_factory: ConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def submit(self, request: TransferRequest) -> TransferResult:
        """Create or safely replay a transfer as one atomic PostgreSQL operation."""

        raise NotImplementedError(
            "PostgreSQL submit behavior will be implemented in the transaction slice."
        )

    def snapshot(self) -> LedgerSnapshot:
        """Return one internally consistent PostgreSQL snapshot."""

        raise NotImplementedError(
            "PostgreSQL snapshot behavior will be implemented in the transaction slice."
        )
