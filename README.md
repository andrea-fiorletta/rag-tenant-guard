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