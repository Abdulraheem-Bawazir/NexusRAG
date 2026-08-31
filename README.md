# NexusRAG

> A production-style, local-first Retrieval-Augmented Generation system for private document knowledge bases.

NexusRAG is an AI engineering portfolio project focused on building the core components of a modern Retrieval-Augmented Generation (RAG) system from the ground up.

Rather than hiding the pipeline behind a high-level RAG framework, NexusRAG implements the major components explicitly so they remain understandable, testable, replaceable, and measurable.

The project currently includes document ingestion, metadata-aware chunking, local embeddings, persistent vector storage, semantic retrieval, BM25 keyword search, hybrid retrieval, filtering, thresholds, and a pluggable reranking layer.

The next major stage is grounded LLM answer generation with traceable citations.

---

## Current Status

### Phase 5 - Retrieval Engine

**Status: Complete**

Current verification:

```text
pytest: 117 passed
ruff:   All checks passed
```

The retrieval system currently supports:

- semantic vector retrieval
- BM25 keyword retrieval
- Reciprocal Rank Fusion (RRF)
- configurable `top_k`
- semantic distance thresholds
- keyword score thresholds
- document filtering
- source filtering
- file-type filtering
- deterministic result ordering
- optional reranking abstraction
- persistent ChromaDB storage
- real semantic retrieval verification
- real hybrid retrieval verification

No answer-generation accuracy percentage is claimed because the LLM generation and formal RAG evaluation stages have not yet been completed.

---

## Current RAG Pipeline

```text
PDF / DOCX / TXT
        |
        v
Document Ingestion
        |
        v
Normalized Document
        |
        v
Chunking
        |
        v
Chunk Objects
        |
        +--------------------------+
        |                          |
        v                          v
Local Embeddings               BM25 Index
        |                          |
        v                          |
Persistent ChromaDB                |
        |                          |
        v                          |
Semantic Retrieval                 |
        |                          |
        +------------+-------------+
                     |
                     v
             Reciprocal Rank
                Fusion (RRF)
                     |
                     v
             Optional Reranker
                     |
                     v
              Ranked Context
                     |
                     v
             LLM Generation
                [NEXT]
                     |
                     v
           Answer + Citations
                [PLANNED]
```

---

# Implemented Phases

## Phase 1 - Foundation

The initial project engineering foundation includes:

- Python 3.11+
- structured Python package layout
- virtual environment workflow
- `pyproject.toml`
- application configuration
- logging configuration
- pytest infrastructure
- Ruff linting
- Git and GitHub repository workflow

---

## Phase 2 - Document Ingestion

NexusRAG supports three source formats:

- TXT
- DOCX
- PDF

All file types are converted into a normalized internal `Document` representation.

### Normalized Document Model

Conceptually:

```python
Document(
    id="...",
    text="...",
    source="handbook.pdf",
    file_type="pdf",
    metadata={
        "page_number": 14,
        "source_id": "...",
        "source_path": "...",
    },
)
```

The model validates:

- document IDs
- document text
- source names
- supported file types
- normalized file-type values

### TXT Loading

TXT files are decoded using UTF-8 with BOM support.

```text
example.txt
    |
    v
TXT Loader
    |
    v
Document
```

### DOCX Loading

DOCX files are parsed using `python-docx`.

Empty paragraphs are removed while meaningful text boundaries are preserved.

```text
example.docx
     |
     v
DOCX Loader
     |
     v
Document
```

### PDF Loading

PDF files are parsed using `pypdf`.

Instead of merging an entire PDF into a single text block, NexusRAG creates normalized page-aware document objects for non-empty pages.

```text
handbook.pdf
     |
     +-- Page 1 -> Document
     +-- Page 2 -> Document
     +-- Page 3 -> Document
     +-- ...
```

This allows page metadata to survive later retrieval stages and eventually support citations such as:

```text
handbook.pdf, page 14
```

Scanned image-only PDFs are not currently processed with OCR.

---

## Unified Document Loading

Downstream RAG components do not need to know how each file format is parsed.

NexusRAG exposes a unified loader:

```python
from app.rag.loaders.document_loader import load_document

documents = load_document("data/raw/example.pdf")
```

The common output is:

```python
list[Document]
```

Conceptually:

```text
TXT  ----\
DOCX -----+--> load_document() --> list[Document]
PDF  ----/
```

---

## Phase 3 - Chunking & Metadata Pipeline

Phase 3 transforms normalized documents into retrieval-ready chunks.

### Implemented

- `Chunk` data model
- configurable character-based chunk size
- configurable chunk overlap
- deterministic SHA-256 chunk IDs
- sequential chunk indexes
- `Document -> Chunk` conversion
- source preservation
- file-type preservation
- metadata preservation
- deep-copy metadata isolation
- empty-text handling
- chunk-boundary edge-case handling
- package-level chunking API

### Chunking Flow

```text
Document
    |
    v
TextChunker
    |
    v
Overlapping Text Segments
    |
    v
Deterministic Chunk IDs
    |
    v
Chunk Objects
    |
    v
Retrieval-Ready Data
```

Chunk IDs are deterministic.

The same:

```text
document ID
+ chunk index
+ chunk text
```

produces the same SHA-256-based chunk ID across repeated runs.

This supports duplicate-safe indexing in the vector database.

---

## Phase 4 - Embeddings & Vector Store

Phase 4 adds semantic vector representation and persistent local vector storage.

### Embedding Architecture

NexusRAG defines an `EmbeddingProvider` interface rather than coupling the system directly to one model implementation.

Current local implementation:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Properties:

```text
Embedding dimension: 384
Execution: local
Paid API required: no
```

### Embedding Pipeline

```text
Chunk
  |
  v
Sentence Transformer
  |
  v
384-dimensional normalized vector
  |
  v
EmbeddedChunk
```

The embedding layer supports:

- single-text embeddings
- batch embeddings
- dimension validation
- provider abstraction
- local Sentence Transformers inference

### Vector Store

NexusRAG currently uses:

```text
ChromaDB
```

with persistent local storage.

Implemented vector-store operations include:

- upsert chunks
- persistent collections
- vector similarity search
- count indexed chunks
- delete chunks by ID
- delete all chunks belonging to one document
- clear a collection
- metadata preservation
- source preservation
- duplicate-safe re-indexing
- metadata filters

Because chunk IDs are deterministic and Chroma uses `upsert`, re-indexing identical chunks does not create unnecessary duplicate records.

---

## Real Semantic Retrieval Verification

A real local semantic retrieval test was performed using:

```text
Question:
Can employees work from home?
```

The highest-ranked result was:

```text
Source:
remote_work_policy.txt

Text:
Employees may work remotely up to three days per week.
Remote work must be approved by the employee's manager.
```

This verifies semantic matching between:

```text
"work from home"
```

and:

```text
"work remotely"
```

even though the wording is different.

The verification runs locally using MiniLM embeddings and ChromaDB.

---

## Phase 5 - Retrieval Engine

Phase 5 converts the low-level vector-search functionality into a full retrieval subsystem.

### Semantic Retrieval

The `SemanticRetriever` handles:

- query validation
- query embeddings
- top-k retrieval
- Chroma vector search
- typed retrieval results
- distance thresholds
- metadata filters

Example conceptually:

```python
results = semantic_retriever.retrieve(
    query="Can employees work from home?",
    top_k=5,
)
```

### Distance Thresholds

Vector databases will usually return the nearest result even when that result is weak.

NexusRAG therefore supports configurable distance thresholds.

```text
Query
  |
  v
Semantic Retrieval
  |
  v
Distance Check
  |
  +-- strong enough --> keep
  |
  +-- too weak ------> reject
```

This will later help prevent unsupported LLM answers.

### Metadata Filtering

Semantic retrieval can be restricted using:

- `document_id`
- `source`
- `file_type`

Example:

```python
results = semantic_retriever.retrieve(
    query="What is the policy?",
    document_id="doc-001",
)
```

---

## BM25 Keyword Retrieval

Semantic search is useful when wording differs.

Keyword retrieval is useful for:

- exact terms
- product names
- policy identifiers
- error codes
- acronyms
- technical terminology

NexusRAG uses:

```text
rank-bm25
```

with BM25Okapi.

Example:

```text
TRV-8842
```

can be retrieved directly through lexical matching even if semantic similarity alone is less reliable.

---

## Hybrid Retrieval

NexusRAG combines semantic retrieval and BM25 retrieval.

```text
Semantic Retriever
        |
        |
        +---------+
                  |
                  v
                RRF
                  ^
                  |
        +---------+
        |
BM25 Retriever
```

The system uses **Reciprocal Rank Fusion (RRF)**.

RRF is used instead of directly combining raw scores because:

```text
Chroma distance
```

and:

```text
BM25 score
```

are on different numerical scales and are not directly comparable.

RRF operates on ranking positions instead.

A chunk appearing highly in both systems receives a stronger fused score.

---

## Reranking Architecture

NexusRAG includes a pluggable:

```text
Reranker
```

protocol.

Current implementation:

```text
NoOpReranker
```

The current implementation preserves the existing hybrid ranking.

This abstraction allows a stronger local reranker, such as a cross-encoder, to be added later without redesigning the retrieval system.

A learned cross-encoder reranker has **not** yet been implemented, so the project does not claim that capability.

---

## Real Hybrid Retrieval Verification

The full retrieval pipeline has been tested with real local components.

### Semantic Question

```text
Can employees work from home?
```

Expected source:

```text
remote_work_policy.txt
```

### Exact-Term Question

```text
What does policy TRV-8842 require?
```

Expected source:

```text
travel_policy.txt
```

The verification combines:

```text
MiniLM embeddings
+
ChromaDB semantic search
+
BM25 keyword search
+
Reciprocal Rank Fusion
+
NoOp reranking interface
```

This demonstrates both semantic and exact-term retrieval behavior.

---

# Current Project Structure

```text
NexusRAG/
|
+-- app/
|   |
|   +-- api/
|   |
|   +-- core/
|   |   +-- config.py
|   |   +-- logging_config.py
|   |
|   +-- models/
|   |   +-- chunk.py
|   |   +-- document.py
|   |   +-- embedded_chunk.py
|   |   +-- hybrid_retrieval_result.py
|   |   +-- keyword_retrieval_result.py
|   |   +-- retrieval_result.py
|   |
|   +-- rag/
|       |
|       +-- chunking/
|       |   +-- chunk_id.py
|       |   +-- document_chunker.py
|       |   +-- text_chunker.py
|       |
|       +-- embeddings/
|       |   +-- base.py
|       |   +-- chunk_embedder.py
|       |   +-- sentence_transformer.py
|       |
|       +-- loaders/
|       |   +-- document_loader.py
|       |   +-- docx_loader.py
|       |   +-- pdf_loader.py
|       |   +-- txt_loader.py
|       |
|       +-- retrieval/
|       |   +-- hybrid_retriever.py
|       |   +-- keyword_retriever.py
|       |   +-- reranker.py
|       |   +-- semantic_retriever.py
|       |
|       +-- vector_store/
|           +-- chroma_store.py
|
+-- data/
|   +-- raw/
|   +-- processed/
|
+-- scripts/
|   +-- verify_embeddings.py
|   +-- verify_hybrid_retrieval.py
|   +-- verify_semantic_retrieval.py
|
+-- tests/
|   +-- models/
|   +-- rag/
|       +-- chunking/
|       +-- embeddings/
|       +-- loaders/
|       +-- retrieval/
|       +-- vector_store/
|
+-- docs/
|   +-- nexusrag_roadmap.html
|
+-- .gitignore
+-- pyproject.toml
+-- README.md
```

The architecture will continue evolving as answer generation, citations, APIs, evaluation, and deployment are added.

---

# Installation

## Requirements

- Python 3.11+
- Git

Clone the repository:

```bash
git clone <repository-url>
cd NexusRAG
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install NexusRAG with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

---

# Current Technology Stack

## Runtime

```text
Python
pypdf
python-docx
sentence-transformers
ChromaDB
rank-bm25
```

## Development / Testing

```text
pytest
Ruff
ReportLab
Git
GitHub
```

## Current Local AI Components

```text
Embedding model:
sentence-transformers/all-MiniLM-L6-v2

Embedding dimension:
384

Vector store:
ChromaDB

Lexical retrieval:
BM25Okapi

Hybrid fusion:
Reciprocal Rank Fusion
```

---

# Running Tests

Run the complete test suite:

```bash
pytest
```

Verbose:

```bash
pytest -v
```

Current verified status:

```text
117 passed
```

Run linting:

```bash
python -m ruff check .
```

Expected:

```text
All checks passed!
```

---

# Verification Scripts

## Real Embeddings

```bash
python scripts/verify_embeddings.py
```

Verifies:

- the real local embedding model loads
- vector dimension is 384
- embeddings are generated correctly

## Real Semantic Retrieval

```bash
python scripts/verify_semantic_retrieval.py
```

Verifies:

```text
"work from home"
```

retrieves the source containing:

```text
"work remotely"
```

## Real Hybrid Retrieval

```bash
python scripts/verify_hybrid_retrieval.py
```

Verifies both:

- semantic retrieval behavior
- exact-term BM25 behavior
- hybrid RRF ranking

---

# Configuration

NexusRAG includes a central application configuration layer.

Current environment settings include values such as:

```text
NEXUSRAG_APP_NAME
NEXUSRAG_ENV
NEXUSRAG_LOG_LEVEL
```

Filesystem paths are resolved relative to the project root instead of being hardcoded to one machine.

This is important for:

- local development
- automated tests
- Docker
- CI
- deployment

---

# Logging

NexusRAG uses Python's standard logging system rather than relying on scattered `print()` statements.

Future production-style logging can include events such as:

```text
INFO | document loaded
INFO | chunks created
INFO | embeddings generated
INFO | vector index updated
INFO | retrieval candidates returned
INFO | hybrid ranking completed
```

Observability will be expanded later in the project.

---

# Private Document Safety

Private input files are stored under:

```text
data/raw/
data/processed/
```

These directories are excluded from Git except for placeholder files.

Local Chroma verification databases are also excluded.

Environment files and virtual environments are excluded:

```text
.env
.venv/
```

Private documents, local vector indexes, and secrets should never be committed to the public repository.

---

# Development Roadmap

## Foundation

- [x] Project architecture
- [x] Python virtual environment
- [x] Git repository
- [x] `pyproject.toml`
- [x] Application configuration
- [x] Logging
- [x] pytest infrastructure
- [x] Ruff linting

## Document Ingestion

- [x] Normalized `Document` model
- [x] TXT loader
- [x] PDF loader
- [x] Page-aware PDF metadata
- [x] DOCX loader
- [x] Unified document loader
- [x] Ingestion tests

## Chunking

- [x] `Chunk` model
- [x] Configurable character chunking
- [x] Chunk overlap
- [x] Deterministic chunk IDs
- [x] Metadata propagation
- [x] Deep-copy metadata isolation
- [x] Chunking tests

## Embeddings and Vector Storage

- [x] Embedding provider abstraction
- [x] Local MiniLM embedding model
- [x] Batch chunk embedding
- [x] Embedding dimension validation
- [x] Persistent ChromaDB storage
- [x] Duplicate-safe upserts
- [x] Vector similarity queries
- [x] Document deletion
- [x] Collection clearing
- [x] Metadata filtering
- [x] Persistence testing

## Retrieval Engine

- [x] Semantic retrieval
- [x] Configurable top-k
- [x] Distance thresholds
- [x] Metadata filtering
- [x] BM25 keyword retrieval
- [x] Keyword score thresholds
- [x] Reciprocal Rank Fusion
- [x] Hybrid retrieval
- [x] Deterministic fused ordering
- [x] Reranker abstraction
- [x] End-to-end semantic verification
- [x] End-to-end hybrid verification

## Grounded Generation

- [ ] LLM provider abstraction
- [ ] Grounded RAG prompt
- [ ] Context construction
- [ ] Context limits
- [ ] Answer generation
- [ ] Source citations
- [ ] Insufficient-evidence behavior

## Evaluation

- [ ] Retrieval evaluation dataset
- [ ] Recall@K / Hit Rate
- [ ] MRR
- [ ] Citation correctness
- [ ] Groundedness evaluation
- [ ] Unsupported-question testing
- [ ] Benchmark reporting

## Application Layer

- [ ] FastAPI backend
- [ ] REST endpoints
- [ ] Document upload API
- [ ] Query API
- [ ] Interactive web interface
- [ ] Source inspection UI
- [ ] Streaming responses

## AI Tooling

- [ ] MCP server
- [ ] MCP document-search tools

## Production Engineering

- [ ] Structured end-to-end logging
- [ ] Request IDs
- [ ] Latency measurement
- [ ] Docker
- [ ] Docker Compose
- [ ] GitHub Actions CI
- [ ] Deployment
- [ ] Monitoring and observability

## Portfolio Presentation

- [ ] Final architecture diagram
- [ ] Retrieval benchmarks
- [ ] Evaluation results
- [ ] API documentation
- [ ] Screenshots
- [ ] Demo video
- [ ] Deployment documentation
- [ ] Technical case study
- [ ] Final release

---

# Engineering Principles

## Understand Before Abstracting

Core RAG components are implemented explicitly before introducing higher-level frameworks.

## Replaceable Components

Embeddings, retrieval methods, rerankers, vector stores, and future LLM providers should expose stable interfaces.

## Preserve Metadata

Source information must survive:

```text
ingestion
-> chunking
-> indexing
-> retrieval
-> generation
-> citations
```

## Test Behavior

Tests validate expected behavior, edge cases, data integrity, and component contracts rather than only verifying that code executes.

## Local-First Development

Core RAG functionality should work without requiring paid external APIs.

## Measure Before Claiming

Performance and accuracy claims will only be published after controlled evaluation.

## Incremental Architecture

Complex abstractions are introduced only when they provide a concrete engineering benefit.

---

# Next Phase

## Phase 6 - Grounded Answer Generation and Citations

The next stage will connect retrieved evidence to an LLM.

Target pipeline:

```text
User Question
      |
      v
Hybrid Retrieval
      |
      v
Top Evidence
      |
      v
Context Builder
      |
      v
Grounded Prompt
      |
      v
LLM
      |
      v
Answer
      |
      v
Traceable Citations
```

The LLM will be instructed to answer only from retrieved evidence and to return an insufficient-evidence response when the indexed documents do not support an answer.

---

# Project Goal

The final NexusRAG system will allow users to:

1. upload private documents
2. parse and normalize those documents
3. split them into retrieval-ready chunks
4. create local embeddings
5. persist vectors locally
6. perform semantic and keyword retrieval
7. combine results using hybrid retrieval
8. optionally rerank retrieved evidence
9. generate grounded answers
10. inspect traceable citations
11. evaluate retrieval and answer quality
12. interact through an API and web interface
13. deploy the system reproducibly

NexusRAG is being built as a serious AI engineering portfolio project with emphasis on retrieval systems, software architecture, testing, evaluation, APIs, deployment, and production engineering rather than only model usage.