# rag-tenant-guard

<div align="center">

**Il fail-closed gate per RAG multi-tenant.**

Isola i tenant, valida gli scope e impedisce che dati del posto sbagliato
raggiungano il prompt dell'LLM.

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Zero dependencies](https://img.shields.io/badge/dependencies-0-6E40C9?style=for-the-badge)](pyproject.toml)
[![Mypy strict](https://img.shields.io/badge/mypy-strict-00A3E0?style=for-the-badge)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E?style=for-the-badge)](LICENSE)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=22&duration=3000&pause=700&color=64FFDA&center=true&vCenter=true&width=760&lines=Tenant+A...+Tenant+B...+Zero+leakage.;Scope+validato+prima+del+prompt.;RAG+multi-tenant%2C+per+d+e+s+i+g+n.">
  <img alt="rag-tenant-guard: zero cross-tenant leakage" src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=22&duration=3000&pause=700&color=0F766E&center=true&vCenter=true&width=760&lines=Tenant+A...+Tenant+B...+Zero+leakage.;Scope+validato+prima+del+prompt.;RAG+multi-tenant%2C+per+d+e+s+i+g+n.">
</picture>

</div>

---

## Perché esiste

Nei sistemi RAG multi-tenant, un filtro non correttamente applicato può combinare
chunk privati di tenant diversi nello stesso contesto.

`rag-tenant-guard` mette una barriera deterministica tra retriever e LLM:

```mermaid
%%{init: {'theme':'base','themeVariables': {'primaryColor':'#111827','primaryTextColor':'#F8FAFC','primaryBorderColor':'#64FFDA','lineColor':'#64FFDA','secondaryColor':'#0F766E','tertiaryColor':'#1E293B','fontFamily':'monospace'}}}%%
flowchart LR
    A([Vector DB]) -->|chunk recuperati| B{Guarda il tenant}
    B -->|ID diverso| X[Reject]
    B -->|ID uguale| C{Scope autorizzato?}
    C -->|No| X
    C -->|Si| D([Contesto sicuro])
    D --> E([LLM / Prompt])

    X -.->|blocked_count| R[Audit]

    style A fill:#1E293B,stroke:#94A3B8,color:#F8FAFC
    style B fill:#7C3AED,stroke:#C4B5FD,color:#FFFFFF
    style C fill:#7C3AED,stroke:#C4B5FD,color:#FFFFFF
    style D fill:#0F766E,stroke:#5EEAD4,color:#FFFFFF
    style E fill:#0F766E,stroke:#5EEAD4,color:#FFFFFF
    style X fill:#991B1B,stroke:#FCA5A5,color:#FFFFFF
    style R fill:#334155,stroke:#94A3B8,color:#F8FAFC
```

<div align="center">

`NON PASSA` &#8594; Tenant mismatch &nbsp;&nbsp;|&nbsp;&nbsp; `NON PASSA` &#8594; Scope mancante o non autorizzato

</div>

---

## Cosa garantisce

| Protezione | Comportamento |
|---|---|
| Isolamento tenant | Il `chunk.tenant_id` deve essere identico al `TenantContext.tenant_id` |
| Identità valida | Tenant vuoti o circondati da spazi vengono rifiutati |
| Isolamento scope | Quando `allowed_scopes` è configurato, il metadata `scope` deve essere presente e autorizzato |
| Modalità filter | Restituisce i chunk ammessi e conta quelli bloccati |
| Modalità strict | Interrompe al primo chunk che viola tenant o scope |
| Modelli protetti | I dataclass usano `frozen=True` e `slots=True` |
| Zero dipendenze | Nessuna libreria runtime esterna |

---

## Quickstart

### Installazione

```bash
git clone https://github.com/andrea-fiorletta/rag-tenant-guard.git
cd rag-tenant-guard

python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
```

Su macOS o Linux:

```bash
source .venv/bin/activate
```

### Filter mode

```python
from rag_tenant_guard.isolation import enforce_tenant_isolation
from rag_tenant_guard.models import DocumentChunk, TenantContext

context = TenantContext(
    tenant_id="tenant-acme",
    allowed_scopes=frozenset({"public", "internal"}),
)

chunks = (
    DocumentChunk(
        chunk_id="chunk-01",
        tenant_id="tenant-acme",
        content="Il rollout è previsto per lunedì.",
        metadata={"scope": "internal"},
        score=0.94,
    ),
    DocumentChunk(
        chunk_id="chunk-02",
        tenant_id="tenant-other",
        content="Dati riservati di un altro tenant.",
        metadata={"scope": "internal"},
        score=0.91,
    ),
)

allowed, blocked_count = enforce_tenant_isolation(context, chunks)

assert len(allowed) == 1
assert blocked_count == 1
```

### Strict mode

```python
from rag_tenant_guard.isolation import enforce_tenant_isolation
from rag_tenant_guard.models import (
    DocumentChunk,
    TenantContext,
    TenantIsolationError,
)

context = TenantContext(
    tenant_id="tenant-acme",
    allowed_scopes=frozenset({"public"}),
)

try:
    enforce_tenant_isolation(
        context,
        (
            DocumentChunk(
                chunk_id="chunk-02",
                tenant_id="tenant-other",
                content="Non dovrebbe superare il gate.",
                metadata={"scope": "public"},
            ),
        ),
        strict=True,
    )
except TenantIsolationError as error:
    print(error)
```

Il messaggio usa l'ID del chunk e la motivazione del rifiuto, senza esporre il
contenuto del documento.

---

## Esempio di decisione

```mermaid
%%{init: {'theme':'base','themeVariables': {'actorBkg':'#1E293B','actorBorder':'#64FFDA','actorTextColor':'#F8FAFC','signalColor':'#64FFDA','labelBoxBkgColor':'#7C3AED','labelBoxBorderColor':'#C4B5FD','labelTextColor':'#FFFFFF','loopTextColor':'#F8FAFC','noteBkgColor':'#0F766E','noteBorderColor':'#5EEAD4','noteTextColor':'#FFFFFF','fontFamily':'monospace'}}}%%
sequenceDiagram
    autonumber
    participant R as Retriever
    participant G as Tenant Guard
    participant L as LLM

    R->>G: chunk[] + TenantContext

    loop Per ogni chunk
        G->>G: valida tenant_id
        alt ID diverso
            G-->>R: reject + +1 blocked
        else ID uguale
            G->>G: valida scope
            alt Scope autorizzato
                G-->>R: keep
            else Scope vietato
                G-->>R: reject + +1 blocked
            end
        end
    end

    R->>L: solo chunk ammessi
```

### Modalità disponibili

```python
# Filter mode: continua e restituisce il conteggio dei blocchi
allowed, blocked_count = enforce_tenant_isolation(context, chunks)

# Strict mode: solleva TenantIsolationError al primo chunk non valido
allowed, blocked_count = enforce_tenant_isolation(
    context,
    chunks,
    strict=True,
)
```

> Quando `allowed_scopes` è una frozenset vuota, il controllo scope viene ignorato.
> Per un RAG multi-tenant, configura sempre gli scope autorizzati.

---

## Modelli principali

```text
TenantContext
├── tenant_id: str
└── allowed_scopes: frozenset[str]

DocumentChunk
├── chunk_id: str
├── tenant_id: str
├── content: str
├── metadata: dict[str, str]
└── score: float

GuardResult
├── tenant_id: str
├── allowed_chunks: tuple[DocumentChunk, ...]
├── blocked_count: int
└── redactions_count: int
```

Eccezioni disponibili:

- `GuardError`
- `InvalidTenantError`
- `TenantIsolationError`

Modello dati PII:

- `RedactionMatch`

`RedactionMatch` è il modello dati relativo alle occorrenze PII, ma il motore di
redazione e l'orchestratore completo non sono ancora implementati.

---

## Struttura del progetto

```text
rag-tenant-guard/
├── src/
│   └── rag_tenant_guard/
│       ├── __init__.py
│       ├── isolation.py
│       └── models.py
├── tests/
│   ├── __init__.py
│   └── test_isolation.py
├── pyproject.toml
├── LICENSE
└── README.md
```

---

## Qualita e sviluppo

Il progetto usa Python 3.12, Ruff, Mypy strict e pytest.

```bash
ruff format --check src tests
ruff check src tests
mypy src
pytest
```

Il pacchetto non ha dipendenze runtime:

```toml
dependencies = []
requires-python = ">=3.12"
```

---

## Roadmap

- [x] Dataclass immutabili e gerarchia delle eccezioni
- [x] Validazione tenant e scope
- [x] Modalita filter e strict
- [ ] Motore deterministico PII
- [ ] Redazione dei chunk prima del prompt
- [ ] Risultato end-to-end tramite `GuardResult`
- [ ] CLI per ispezione locale
- [ ] CI su GitHub Actions

---

## Licenza

Distribuito con licenza [MIT](LICENSE).

<div align="center">

**Dati degli altri tenant = mai nel tuo prompt.**

</div>
