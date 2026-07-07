from __future__ import annotations

import re
from pathlib import Path

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "infra"
    / "postgres"
    / "migrations"
    / "0001_ledger_schema.sql"
)


def test_schema_declares_the_required_ledger_tables() -> None:
    schema = _compact_schema()

    for table_name in (
        "transfers",
        "idempotency_records",
        "ledger_entries",
        "audit_records",
    ):
        assert f"create table {table_name} (" in schema


def test_transfers_enforce_the_core_transfer_invariants() -> None:
    schema = _compact_schema()

    assert "id text primary key check (btrim(id) <> '')" in schema
    assert (
        "request_fingerprint text not null check (request_fingerprint ~ '^[0-9a-f]{64}$')" in schema
    )
    assert "amount numeric(18, 2) not null check (amount > 0)" in schema
    assert "currency ~ '^[A-Z]{3}$'" in _schema()
    assert (
        "constraint transfers_distinct_accounts check (debit_account_id <> credit_account_id)"
        in schema
    )
    assert "created_at timestamptz not null" in schema


def test_idempotency_records_are_unique_and_reference_one_transfer() -> None:
    schema = _compact_schema()

    assert "key text primary key check (btrim(key) <> '')" in schema
    assert "transfer_id text not null unique references transfers (id) on delete restrict" in schema
    assert schema.count("request_fingerprint text not null") == 2


def test_ledger_entries_enforce_one_debit_and_one_credit_slot_per_transfer() -> None:
    schema = _compact_schema()

    assert "direction text not null check (direction in ('debit', 'credit'))" in schema
    assert (
        "constraint ledger_entries_one_direction_per_transfer unique (transfer_id, direction)"
        in schema
    )
    assert "references transfers (id) on delete restrict" in schema


def test_audit_records_are_unique_per_transfer_and_use_the_expected_event_type() -> None:
    schema = _compact_schema()

    assert "transfer_id text not null references transfers (id) on delete restrict" in schema
    assert "event_type text not null check (event_type = 'transfer_accepted')" in schema
    assert "constraint audit_records_one_per_transfer" in schema
    assert "occurred_at timestamptz not null" in schema


def test_schema_has_an_index_for_ledger_entries_by_transfer_id() -> None:
    schema = _compact_schema()

    assert "create index ledger_entries_by_transfer_id on ledger_entries (transfer_id)" in schema


def _schema() -> str:
    return _SCHEMA_PATH.read_text(encoding="utf-8")


def _compact_schema() -> str:
    return re.sub(r"\s+", " ", _schema()).strip().lower()
