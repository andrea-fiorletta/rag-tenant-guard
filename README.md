<div align="center">

# 🛡️ rag-tenant-guard

**Deterministic cross-tenant isolation & PII redaction boundary for RAG pipelines.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Typing: mypy strict](https://img.shields.io/badge/mypy-strict-blue?style=flat-square)](https://mypy-lang.org/)
[![Code style: ruff](https://img.shields.io/badge/ruff-checked-D7FF64?style=flat-square&logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)
[![CI](https://github.com/andrea-fiorletta/rag-tenant-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/andrea-fiorletta/rag-tenant-guard/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

*Zero-dependency Python security layer that prevents cross-tenant data leakage and strips sensitive PII before retrieved context ever reaches an LLM.*

</div>

---

## Why `rag-tenant-guard`?

In multi-tenant RAG systems, vector databases and retrieval pipelines are a high-risk boundary: a single misconfigured metadata filter or malformed query can leak **Tenant B's private documents** into **Tenant A's prompt**, or send raw PII (emails, API keys, payment data) to third-party LLM providers.

`rag-tenant-guard` acts as a **strict, deterministic fail-closed gate** between your retriever and your LLM:

```text
[ Vector DB / Retriever ]
           │
           ▼  (Unverified DocumentChunks)
┌─────────────────────────────────────────────────────────┐
│                    rag-tenant-guard                     │
│                                                         │
│  1. Tenant & Scope Isolation  ──▶ Drop or Raise (Strict)│
│  2. PII Redaction Engine      ──▶ Mask Sensitive Tokens │
│  3. Safe Audit Result         ──▶ Zero Content Leakage  │
└─────────────────────────────────────────────────────────┘
           │
           ▼  (Verified, Redacted Context)
    [ LLM Prompt / Agent ]

Key Security GuaranteesLayerProtectionModeTenant BoundaryEnforces exact tenant_id matching and rejects empty/whitespace-padded identifiers.Filter (strict=False) or Fail-Closed (strict=True)Scope AuthorizationValidates chunk scope metadata against an immutable frozenset of allowed scopes.Opt-in via TenantContext.allowed_scopesPII RedactionDetects and masks sensitive entities (EMAIL, API_KEY, CREDIT_CARD, etc.) before LLM ingestion.Deterministic compiled regex engineZero-Leakage ErrorsExceptions and audit metadata never log raw chunk.content or foreign tenant_id values.Always enforcedImmutable ModelsAll boundary objects use @dataclass(frozen=True, slots=True) to prevent runtime mutation.Always enforcedQuickstartInstallationBashgit clone git@github.com:andrea-fiorletta/rag-tenant-guard.git
cd rag-tenant-guard
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -e .
UsagePythonfrom rag_tenant_guard.models import DocumentChunk, TenantContext
from rag_tenant_guard.isolation import enforce_tenant_isolation

context = TenantContext(
    tenant_id="tenant_acme",
    allowed_scopes=frozenset({"public", "internal"}),
)

retrieved_chunks = [
    DocumentChunk(
        chunk_id="chk_01",
        tenant_id="tenant_acme",
        content="Q4 roadmap approved by engineering.",
        metadata={"scope": "internal"},
        score=0.94,
    ),
    DocumentChunk(
        chunk_id="chk_02",
        tenant_id="tenant_other",  # Cross-tenant leak attempt
        content="Confidential merger details.",
        metadata={"scope": "internal"},
        score=0.91,
    ),
]

allowed, blocked_count = enforce_tenant_isolation(
    context,
    retrieved_chunks,
    strict=False,  # Set strict=True to raise TenantIsolationError immediately
)

print(f"Allowed: {len(allowed)} | Blocked: {blocked_count}")
# Output: Allowed: 1 | Blocked: 1
Project StructurePlaintextrag-tenant-guard/
├── .github/
│   └── workflows/
│       └── ci.yml                  # Automated ruff, mypy --strict & pytest gates
├── src/
│   └── rag_tenant_guard/
│       ├── __init__.py
│       ├── models.py               # Immutable dataclasses & custom exception hierarchy
│       ├── isolation.py            # Strict cross-tenant & scope isolation boundary
│       ├── pii.py                  # Deterministic PII detection & redaction engine
│       ├── guard.py                # End-to-end pipeline orchestrator
│       └── cli.py                  # Terminal entrypoint for payload inspection
├── tests/
│   ├── test_isolation.py           # Unit tests for tenant & scope boundaries
│   ├── test_pii.py                 # Unit tests for PII detection & masking
│   └── test_guard_adversarial.py   # Adversarial cross-tenant & leakage test suite
├── pyproject.toml                  # Build, ruff, mypy & pytest configuration
└── README.md
Quality Gates & DevelopmentThis project enforces strict static typing and automated security linting with zero runtime dependencies:Bash# Format & lint
ruff format --check src tests
ruff check src tests

# Strict type checking
mypy src

# Run test suite
pytest
Roadmap[x] Phase 1: Project scaffolding, pyproject.toml, ruff & mypy --strict setup[x] Phase 2: Immutable boundary models (models.py)[ ] Phase 3: Cross-tenant & scope isolation engine (isolation.py)[ ] Phase 4: PII detection & redaction engine (pii.py)[ ] Phase 5: Pipeline orchestrator, adversarial test suite, CLI & GitHub Actions CILicenseDistributed under the MIT License. See LICENSE for details.