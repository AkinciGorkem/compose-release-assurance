-- Synthetic ledger persistence schema for Compose Release Assurance.
-- This migration contains no real customer data, credentials, or environment settings.

CREATE TABLE transfers (
    id TEXT PRIMARY KEY CHECK (btrim(id) <> ''),
    request_fingerprint TEXT NOT NULL
        CHECK (request_fingerprint ~ '^[0-9a-f]{64}$'),
    debit_account_id TEXT NOT NULL CHECK (btrim(debit_account_id) <> ''),
    credit_account_id TEXT NOT NULL CHECK (btrim(credit_account_id) <> ''),
    amount NUMERIC(18, 2) NOT NULL CHECK (amount > 0),
    currency TEXT NOT NULL CHECK (currency ~ '^[A-Z]{3}$'),
    created_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT transfers_distinct_accounts
        CHECK (debit_account_id <> credit_account_id)
);

CREATE TABLE idempotency_records (
    key TEXT PRIMARY KEY CHECK (btrim(key) <> ''),
    request_fingerprint TEXT NOT NULL
        CHECK (request_fingerprint ~ '^[0-9a-f]{64}$'),
    transfer_id TEXT NOT NULL UNIQUE
        REFERENCES transfers (id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE ledger_entries (
    id TEXT PRIMARY KEY CHECK (btrim(id) <> ''),
    transfer_id TEXT NOT NULL
        REFERENCES transfers (id) ON DELETE RESTRICT,
    direction TEXT NOT NULL CHECK (direction IN ('DEBIT', 'CREDIT')),
    account_id TEXT NOT NULL CHECK (btrim(account_id) <> ''),
    amount NUMERIC(18, 2) NOT NULL CHECK (amount > 0),
    currency TEXT NOT NULL CHECK (currency ~ '^[A-Z]{3}$'),
    created_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT ledger_entries_one_direction_per_transfer
        UNIQUE (transfer_id, direction)
);

CREATE TABLE audit_records (
    id TEXT PRIMARY KEY CHECK (btrim(id) <> ''),
    transfer_id TEXT NOT NULL
        REFERENCES transfers (id) ON DELETE RESTRICT,
    event_type TEXT NOT NULL CHECK (event_type = 'TRANSFER_ACCEPTED'),
    correlation_id TEXT CHECK (
        correlation_id IS NULL OR btrim(correlation_id) <> ''
    ),
    occurred_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT audit_records_one_per_transfer UNIQUE (transfer_id)
);

CREATE INDEX ledger_entries_by_transfer_id
    ON ledger_entries (transfer_id);
