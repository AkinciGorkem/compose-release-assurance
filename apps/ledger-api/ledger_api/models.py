"""Immutable value objects and entities for the synthetic ledger domain."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from hashlib import sha256

from ledger_api.errors import DomainValidationError


class EntryDirection(StrEnum):
    """Direction of a double-entry ledger record."""

    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


@dataclass(frozen=True, slots=True)
class TransferRequest:
    """Validated synthetic transfer input.

    The idempotency fingerprint intentionally excludes correlation_id because it
    is operational metadata rather than a business field.
    """

    idempotency_key: str
    debit_account_id: str
    credit_account_id: str
    amount: Decimal
    currency: str
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        idempotency_key = _required_text(self.idempotency_key, "idempotency_key")
        debit_account_id = _required_text(self.debit_account_id, "debit_account_id")
        credit_account_id = _required_text(self.credit_account_id, "credit_account_id")
        currency = _validate_currency(self.currency)
        correlation_id = _optional_text(self.correlation_id, "correlation_id")

        if not isinstance(self.amount, Decimal):
            raise DomainValidationError("amount must be a Decimal value.")

        if not self.amount.is_finite() or self.amount <= Decimal("0"):
            raise DomainValidationError("amount must be a finite positive Decimal value.")

        exponent = self.amount.as_tuple().exponent
        if not isinstance(exponent, int) or exponent < -2:
            raise DomainValidationError("amount must use no more than two decimal places.")

        if debit_account_id == credit_account_id:
            raise DomainValidationError(
                "debit_account_id and credit_account_id must identify different accounts."
            )

        object.__setattr__(self, "idempotency_key", idempotency_key)
        object.__setattr__(self, "debit_account_id", debit_account_id)
        object.__setattr__(self, "credit_account_id", credit_account_id)
        object.__setattr__(self, "currency", currency)
        object.__setattr__(self, "correlation_id", correlation_id)

    @property
    def fingerprint(self) -> str:
        """Return a deterministic fingerprint of the transfer's business fields."""

        canonical_payload = json.dumps(
            [
                self.debit_account_id,
                self.credit_account_id,
                _canonical_amount(self.amount),
                self.currency,
            ],
            ensure_ascii=True,
            separators=(",", ":"),
        )
        return sha256(canonical_payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class Transfer:
    """Accepted synthetic transfer."""

    id: str
    idempotency_key: str
    request_fingerprint: str
    debit_account_id: str
    credit_account_id: str
    amount: Decimal
    currency: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    """One immutable debit or credit record belonging to a transfer."""

    id: str
    transfer_id: str
    direction: EntryDirection
    account_id: str
    amount: Decimal
    currency: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """Audit record produced when a synthetic transfer is accepted."""

    id: str
    transfer_id: str
    event_type: str
    correlation_id: str | None
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class IdempotencyRecord:
    """Mapping between an idempotency key, request fingerprint, and transfer."""

    key: str
    request_fingerprint: str
    transfer_id: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class LedgerSnapshot:
    """Read-only view of the in-memory synthetic ledger state."""

    transfers: tuple[Transfer, ...]
    ledger_entries: tuple[LedgerEntry, ...]
    audit_records: tuple[AuditRecord, ...]
    idempotency_records: tuple[IdempotencyRecord, ...]


@dataclass(frozen=True, slots=True)
class TransferResult:
    """Result of accepting a transfer or returning a safe replay."""

    transfer: Transfer
    ledger_entries: tuple[LedgerEntry, ...]
    audit_record: AuditRecord
    replayed: bool


def _required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise DomainValidationError(f"{field_name} must be a string.")

    normalized = value.strip()
    if not normalized:
        raise DomainValidationError(f"{field_name} must not be empty.")

    return normalized


def _optional_text(value: object, field_name: str) -> str | None:
    if value is None:
        return None

    return _required_text(value, field_name)


def _validate_currency(value: object) -> str:
    currency = _required_text(value, "currency")
    is_three_uppercase_ascii_letters = len(currency) == 3 and all(
        "A" <= character <= "Z" for character in currency
    )
    if not is_three_uppercase_ascii_letters:
        raise DomainValidationError("currency must contain exactly three uppercase ASCII letters.")

    return currency


def _canonical_amount(amount: Decimal) -> str:
    return format(amount.normalize(), "f")
