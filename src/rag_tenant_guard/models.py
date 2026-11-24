from dataclasses import dataclass, field


class GuardError(Exception):
    """Base class for tenant isolation and PII guard errors."""


class InvalidTenantError(GuardError):
    """Raised when a tenant ID is empty or malformed."""


class TenantIsolationError(GuardError):
    """Raised when a chunk violates tenant or scope isolation boundaries."""


@dataclass(frozen=True, slots=True)
class TenantContext:
    """Identify a tenant and the scopes it is allowed to use."""

    tenant_id: str
    allowed_scopes: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not self.tenant_id.strip() or self.tenant_id != self.tenant_id.strip():
            raise InvalidTenantError("Tenant ID cannot be empty or have surrounding whitespace.")


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    """Represent a text fragment with tenant, metadata, and relevance score."""

    chunk_id: str
    tenant_id: str
    content: str
    metadata: dict[str, str] = field(default_factory=dict)
    score: float = 0.0


@dataclass(frozen=True, slots=True)
class GuardResult:
    """Summarize allowed chunks and guard decisions for one tenant."""

    tenant_id: str
    allowed_chunks: tuple[DocumentChunk, ...]
    blocked_count: int
    redactions_count: int


@dataclass(frozen=True, slots=True)
class RedactionMatch:
    """Describe one PII occurrence found within a text fragment."""

    start: int
    end: int
    kind: str
