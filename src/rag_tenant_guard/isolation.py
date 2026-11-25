from collections.abc import Iterable

from rag_tenant_guard.models import DocumentChunk, TenantContext, TenantIsolationError


def enforce_tenant_isolation(
    context: TenantContext,
    chunks: Iterable[DocumentChunk],
    *,
    strict: bool = False,
) -> tuple[tuple[DocumentChunk, ...], int]:
    """Filter document chunks based on tenant or scope boundaries."""

    allowed: list[DocumentChunk] = []
    blocked_count = 0

    for chunk in chunks:
        violation_reason: str | None = None

        if not chunk.tenant_id.strip() or chunk.tenant_id != context.tenant_id:
            violation_reason = "Tenant Mismatch"
        elif context.allowed_scopes:
            scope = chunk.metadata.get("scope")
            if scope is None or scope not in context.allowed_scopes:
                violation_reason = "unauthorized scope"

        if violation_reason is not None:
            if strict:
                raise TenantIsolationError(
                    f"Chunk {chunk.chunk_id!r} rejected: {violation_reason}."
                )
            blocked_count += 1
        else:
            allowed.append(chunk)

    return tuple(allowed), blocked_count
