"""PostgreSQL persistence adapter for the synthetic ledger store."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from typing import Any, cast

from psycopg import Connection

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

ConnectionFactory = Callable[[], Connection[Any]]
DatabaseRow = tuple[Any, ...]


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

        with self._connection_factory() as connection:
            with connection.transaction():
                _execute(
                    connection,
                    "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY",
                )

                return LedgerSnapshot(
                    transfers=tuple(
                        _transfer_from_row(row)
                        for row in _fetch_rows(
                            connection,
                            """
                            SELECT
                                transfers.id,
                                idempotency_records.key,
                                transfers.request_fingerprint,
                                transfers.debit_account_id,
                                transfers.credit_account_id,
                                transfers.amount,
                                transfers.currency,
                                transfers.created_at
                            FROM transfers
                            INNER JOIN idempotency_records
                                ON idempotency_records.transfer_id = transfers.id
                            ORDER BY transfers.created_at, transfers.id
                            """,
                        )
                    ),
                    ledger_entries=tuple(
                        _ledger_entry_from_row(row)
                        for row in _fetch_rows(
                            connection,
                            """
                            SELECT
                                id,
                                transfer_id,
                                direction,
                                account_id,
                                amount,
                                currency,
                                created_at
                            FROM ledger_entries
                            ORDER BY transfer_id, direction, id
                            """,
                        )
                    ),
                    audit_records=tuple(
                        _audit_record_from_row(row)
                        for row in _fetch_rows(
                            connection,
                            """
                            SELECT
                                id,
                                transfer_id,
                                event_type,
                                correlation_id,
                                occurred_at
                            FROM audit_records
                            ORDER BY occurred_at, id
                            """,
                        )
                    ),
                    idempotency_records=tuple(
                        _idempotency_record_from_row(row)
                        for row in _fetch_rows(
                            connection,
                            """
                            SELECT
                                key,
                                request_fingerprint,
                                transfer_id,
                                created_at
                            FROM idempotency_records
                            ORDER BY created_at, key
                            """,
                        )
                    ),
                )


def _execute(connection: Connection[Any], statement: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute(statement)


def _fetch_rows(connection: Connection[Any], statement: str) -> tuple[DatabaseRow, ...]:
    with connection.cursor() as cursor:
        cursor.execute(statement)
        return tuple(cast(DatabaseRow, row) for row in cursor.fetchall())


def _transfer_from_row(row: DatabaseRow) -> Transfer:
    _require_row_length(row, 8, "transfers")

    return Transfer(
        id=_require_text(row[0], "transfers.id"),
        idempotency_key=_require_text(row[1], "idempotency_records.key"),
        request_fingerprint=_require_text(row[2], "transfers.request_fingerprint"),
        debit_account_id=_require_text(row[3], "transfers.debit_account_id"),
        credit_account_id=_require_text(row[4], "transfers.credit_account_id"),
        amount=_require_decimal(row[5], "transfers.amount"),
        currency=_require_text(row[6], "transfers.currency"),
        created_at=_require_datetime(row[7], "transfers.created_at"),
    )


def _ledger_entry_from_row(row: DatabaseRow) -> LedgerEntry:
    _require_row_length(row, 7, "ledger_entries")

    return LedgerEntry(
        id=_require_text(row[0], "ledger_entries.id"),
        transfer_id=_require_text(row[1], "ledger_entries.transfer_id"),
        direction=EntryDirection(_require_text(row[2], "ledger_entries.direction")),
        account_id=_require_text(row[3], "ledger_entries.account_id"),
        amount=_require_decimal(row[4], "ledger_entries.amount"),
        currency=_require_text(row[5], "ledger_entries.currency"),
        created_at=_require_datetime(row[6], "ledger_entries.created_at"),
    )


def _audit_record_from_row(row: DatabaseRow) -> AuditRecord:
    _require_row_length(row, 5, "audit_records")

    return AuditRecord(
        id=_require_text(row[0], "audit_records.id"),
        transfer_id=_require_text(row[1], "audit_records.transfer_id"),
        event_type=_require_text(row[2], "audit_records.event_type"),
        correlation_id=_optional_text(row[3], "audit_records.correlation_id"),
        occurred_at=_require_datetime(row[4], "audit_records.occurred_at"),
    )


def _idempotency_record_from_row(row: DatabaseRow) -> IdempotencyRecord:
    _require_row_length(row, 4, "idempotency_records")

    return IdempotencyRecord(
        key=_require_text(row[0], "idempotency_records.key"),
        request_fingerprint=_require_text(row[1], "idempotency_records.request_fingerprint"),
        transfer_id=_require_text(row[2], "idempotency_records.transfer_id"),
        created_at=_require_datetime(row[3], "idempotency_records.created_at"),
    )


def _require_row_length(row: DatabaseRow, expected: int, source: str) -> None:
    if len(row) != expected:
        raise RuntimeError(f"{source} query returned an unexpected column count.")


def _require_text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise RuntimeError(f"{field_name} must be returned as text.")

    return value


def _optional_text(value: object, field_name: str) -> str | None:
    if value is None:
        return None

    return _require_text(value, field_name)


def _require_decimal(value: object, field_name: str) -> Decimal:
    if not isinstance(value, Decimal):
        raise RuntimeError(f"{field_name} must be returned as Decimal.")

    return value


def _require_datetime(value: object, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise RuntimeError(f"{field_name} must be returned as datetime.")

    return value
