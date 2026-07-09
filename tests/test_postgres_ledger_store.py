from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import psycopg
import pytest
from ledger_api import LedgerStore, PostgresLedgerStore, validate_ledger_snapshot
from psycopg import Connection

MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "infra"
    / "postgres"
    / "migrations"
    / "0001_ledger_schema.sql"
)


def test_postgres_ledger_store_satisfies_the_ledger_store_contract() -> None:
    store = PostgresLedgerStore(connection_factory=_unexpected_connection)

    assert isinstance(store, LedgerStore)


def test_postgres_ledger_store_reads_a_valid_snapshot_from_postgresql() -> None:
    dsn = os.environ.get("CRA_POSTGRES_DSN")
    if not dsn:
        pytest.skip("CRA_POSTGRES_DSN is required for PostgreSQL adapter integration tests.")

    _reset_database(dsn)
    _insert_valid_synthetic_transfer(dsn)

    store = PostgresLedgerStore(connection_factory=lambda: psycopg.connect(dsn))
    snapshot = store.snapshot()

    assert len(snapshot.transfers) == 1
    assert len(snapshot.ledger_entries) == 2
    assert len(snapshot.audit_records) == 1
    assert len(snapshot.idempotency_records) == 1

    transfer = snapshot.transfers[0]
    idempotency_record = snapshot.idempotency_records[0]

    assert transfer.id == "transfer-snapshot-001"
    assert transfer.request_fingerprint == "a" * 64
    assert transfer.debit_account_id == "account-debit"
    assert transfer.credit_account_id == "account-credit"
    assert str(transfer.amount) == "25.00"
    assert transfer.currency == "USD"

    assert idempotency_record.key == "retry-snapshot-001"
    assert idempotency_record.transfer_id == transfer.id
    assert idempotency_record.request_fingerprint == transfer.request_fingerprint

    report = validate_ledger_snapshot(snapshot)

    assert report.is_valid is True


def _unexpected_connection() -> Any:
    raise AssertionError("The skeleton contract test must not open a database connection.")


def _reset_database(dsn: str) -> None:
    migration_sql = MIGRATION_PATH.read_text(encoding="utf-8")

    with psycopg.connect(dsn) as connection:
        with connection.transaction():
            _execute(
                connection,
                """
                DROP TABLE IF EXISTS
                    audit_records,
                    ledger_entries,
                    idempotency_records,
                    transfers
                CASCADE
                """,
            )
            _execute(connection, migration_sql)


def _insert_valid_synthetic_transfer(dsn: str) -> None:
    with psycopg.connect(dsn) as connection:
        with connection.transaction():
            _execute(
                connection,
                """
                INSERT INTO transfers (
                    id,
                    request_fingerprint,
                    debit_account_id,
                    credit_account_id,
                    amount,
                    currency,
                    created_at
                )
                VALUES (
                    'transfer-snapshot-001',
                    repeat('a', 64),
                    'account-debit',
                    'account-credit',
                    25.00,
                    'USD',
                    TIMESTAMPTZ '2026-07-09 10:00:00+00'
                )
                """,
            )
            _execute(
                connection,
                """
                INSERT INTO idempotency_records (
                    key,
                    request_fingerprint,
                    transfer_id,
                    created_at
                )
                VALUES (
                    'retry-snapshot-001',
                    repeat('a', 64),
                    'transfer-snapshot-001',
                    TIMESTAMPTZ '2026-07-09 10:00:00+00'
                )
                """,
            )
            _execute(
                connection,
                """
                INSERT INTO ledger_entries (
                    id,
                    transfer_id,
                    direction,
                    account_id,
                    amount,
                    currency,
                    created_at
                )
                VALUES
                    (
                        'entry-snapshot-debit-001',
                        'transfer-snapshot-001',
                        'DEBIT',
                        'account-debit',
                        25.00,
                        'USD',
                        TIMESTAMPTZ '2026-07-09 10:00:00+00'
                    ),
                    (
                        'entry-snapshot-credit-001',
                        'transfer-snapshot-001',
                        'CREDIT',
                        'account-credit',
                        25.00,
                        'USD',
                        TIMESTAMPTZ '2026-07-09 10:00:00+00'
                    )
                """,
            )
            _execute(
                connection,
                """
                INSERT INTO audit_records (
                    id,
                    transfer_id,
                    event_type,
                    correlation_id,
                    occurred_at
                )
                VALUES (
                    'audit-snapshot-001',
                    'transfer-snapshot-001',
                    'TRANSFER_ACCEPTED',
                    'postgres-snapshot-test',
                    TIMESTAMPTZ '2026-07-09 10:00:00+00'
                )
                """,
            )


def _execute(connection: Connection[Any], statement: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute(statement)
