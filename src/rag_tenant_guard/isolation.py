from collections.abc import Iterable

from rag_tenant_guard.models import DocumentChunk, TenantContext, TenantIsolationError


def enforce_tenant_isolation(
    context: TenantContext,
    chunks: Iterable[DocumentChunk],
    *,
    strict: bool = False,
) -> tuple[tuple[DocumentChunk, ...], int]:
    """Filter or reject chunks that violate tenant or scope boundaries."""