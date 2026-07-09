from __future__ import annotations

from typing import Any

from ledger_api import LedgerStore, PostgresLedgerStore


def test_postgres_ledger_store_satisfies_the_ledger_store_contract() -> None:
    store = PostgresLedgerStore(connection_factory=_unexpected_connection)

    assert isinstance(store, LedgerStore)


def _unexpected_connection() -> Any:
    raise AssertionError("The skeleton contract test must not open a database connection.")
