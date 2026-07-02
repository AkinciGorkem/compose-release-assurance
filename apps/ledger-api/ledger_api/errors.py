"""Domain-level errors with explicit, safe messages."""


class LedgerDomainError(Exception):
    """Base class for synthetic ledger domain errors."""


class DomainValidationError(LedgerDomainError):
    """Raised when a transfer request violates a domain rule."""


class IdempotencyConflictError(LedgerDomainError):
    """Raised when one idempotency key is reused for a different request."""
