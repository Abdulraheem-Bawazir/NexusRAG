# NexusRAG

> A production-style, local-first Retrieval-Augmented Generation system for private document knowledge bases.

NexusRAG is an AI engineering project focused on building the core components of a modern **Retrieval-Augmented Generation (RAG)** system from the ground up.

The project is designed to go beyond a basic "chat with PDF" tutorial by demonstrating the engineering surrounding LLM applications: document ingestion, chunking, embeddings, retrieval, reranking, evaluation, APIs, MCP, testing, Docker, deployment, and observability.

The early stages intentionally avoid hiding the RAG pipeline behind high-level frameworks so that the individual components remain understandable, testable, and replaceable.

---

## Current Status

## Phase 4 — Embeddings & Vector Store

Phase 4 adds the semantic indexing layer that converts retrieval-ready chunks into numerical vectors and stores them in a persistent local vector database.

### Implemented

- Pluggable `EmbeddingProvider` interface
- Local Sentence Transformers embedding provider
- `sentence-transformers/all-MiniLM-L6-v2`
- 384-dimensional normalized embeddings
- Single-text and batch embedding support
- `Chunk` → `EmbeddedChunk` pipeline
- Embedding dimension validation
- Persistent local ChromaDB vector store
- Chunk upsert and duplicate-safe indexing
- Vector similarity queries
- Chunk deletion
- Document-level deletion
- Collection clearing
- Source and metadata preservation inside the vector index
- Persistent data across vector-store instances
- Real semantic retrieval verification

### Semantic Indexing Flow

```text
PDF / DOCX / TXT
       ↓
Document
       ↓
Chunking
       ↓
Chunk objects
       ↓
MiniLM embeddings
       ↓
384-dimensional vectors
       ↓
ChromaDB
       ↓
Semantic similarity search

## High-Level Architecture

```text
PDF / DOCX / TXT
        │
        ▼
┌─────────────────────┐
│ Document Ingestion  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Normalized Document │
└─────────┬───────────┘
          │
          ▼
      Chunking
          │
          ▼
      Embeddings
          │
          ▼
    Vector Database
          │
          │
User Question
          │
          ▼
   Query Embedding
          │
          ▼
 Semantic / Hybrid
      Retrieval
          │
          ▼
      Reranking
          │
          ▼
 Relevant Context
          │
          ▼
         LLM
          │
          ▼
 Answer + Citations
          │
          ▼
      Evaluation
```

The following components are currently implemented:

```text
Documents
    ↓
Parsing
    ↓
Normalized Document ✅
```

The remaining pipeline will be added incrementally.

---

## Why NexusRAG?

Many introductory RAG projects look like:

```python
rag = SomeFramework(...)
rag.chat("question")
```

That is useful for prototyping, but it hides many important engineering decisions.

NexusRAG instead exposes the core pipeline:

```text
documents
    ↓
chunks
    ↓
embeddings
    ↓
vectors
    ↓
retrieval
    ↓
context
    ↓
LLM
    ↓
answer
```

Each stage is implemented as an independent, testable component before higher-level abstractions are introduced.

This makes it possible to understand and evaluate decisions such as:

* document parsing strategy
* chunk size and overlap
* metadata propagation
* embedding model selection
* vector database design
* semantic vs hybrid retrieval
* reranking
* context construction
* citation generation
* retrieval quality
* RAG evaluation
* latency and resource usage

---

## Document Ingestion

NexusRAG currently supports three document formats.

### TXT

TXT files are decoded using UTF-8 with BOM support and normalized into the internal `Document` model.

```text
example.txt
    ↓
TXT Loader
    ↓
Document
```

### DOCX

Word documents are parsed using `python-docx`.

Empty paragraphs are removed while meaningful paragraph boundaries are preserved.

```text
example.docx
     ↓
DOCX Loader
     ↓
Document
```

### PDF

PDF files are parsed using `pypdf`.

Instead of merging an entire PDF into one large text block, NexusRAG creates one normalized document object per non-empty page.

```text
handbook.pdf
     │
     ├── Page 1 → Document
     ├── Page 2 → Document
     ├── Page 3 → Document
     └── ...
```

This preserves page metadata for future source citations.

For example:

```text
Answer evidence
      ↓
Retrieved chunk
      ↓
page_number = 14
      ↓
Citation: handbook.pdf, page 14
```

Scanned/image-only PDFs are not currently processed with OCR.

---

## Unified Loading Interface

Downstream components should not need to know how individual file formats are parsed.

NexusRAG therefore exposes a common loader interface:

```python
from app.rag.loaders.document_loader import load_document

documents = load_document("data/raw/example.pdf")
```

Regardless of the source format, the interface returns:

```python
list[Document]
```

Conceptually:

```text
TXT  ──────┐
DOCX ──────┼──→ load_document() ──→ list[Document]
PDF  ──────┘
```

This provides a stable interface for the upcoming chunking pipeline.

---

## Internal Document Model

All supported document formats are converted into a common representation.

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

The model validates incoming data so malformed or empty documents do not silently enter later stages of the RAG pipeline.

---

## Project Structure

```text
NexusRAG/
│
├── app/
│   ├── api/
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── logging_config.py
│   │
│   ├── models/
│   │   └── document.py
│   │
│   └── rag/
│       └── loaders/
│           ├── document_loader.py
│           ├── docx_loader.py
│           ├── pdf_loader.py
│           └── txt_loader.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── scripts/
│
├── tests/
│   ├── models/
│   └── rag/
│       └── loaders/
│
├── .gitignore
├── pyproject.toml
└── README.md
```

The architecture will evolve as additional RAG components are implemented.

---

## Installation

### Requirements

* Python 3.11+
* Git

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

## Running the Tests

Run the full test suite:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

Current status:

```text
29 tests passing
```

The test suite currently covers:

* configuration
* project smoke testing
* `Document` validation
* TXT ingestion
* PDF ingestion
* DOCX ingestion
* file type validation
* missing files
* empty documents
* PDF page metadata
* PDF source identity
* UTF-8 BOM handling
* unified loader routing

---

## Configuration

NexusRAG includes a central application configuration layer.

Settings can be loaded from environment variables while maintaining safe local defaults.

Examples include:

```text
NEXUSRAG_APP_NAME
NEXUSRAG_ENV
NEXUSRAG_LOG_LEVEL
```

Filesystem paths are resolved relative to the project root rather than hardcoded machine-specific paths.

This allows the same codebase to run locally, in tests, inside Docker, or on a deployment server.

---

## Logging

NexusRAG uses Python's standard logging system instead of relying on scattered `print()` statements.

Example future application logs:

```text
INFO | app.rag.loaders.pdf | Loaded document.pdf
INFO | app.rag.chunking | Created 42 chunks
INFO | app.rag.retrieval | Retrieved top 5 candidates
INFO | app.rag.reranking | Reranked 5 candidates
```

Logging will become increasingly important as the system gains APIs, background ingestion, and deployment infrastructure.

---

## Private Document Safety

Files placed inside:

```text
data/raw/
data/processed/
```

are ignored by Git.

This prevents locally ingested or generated documents from accidentally being committed to the public repository.

Only directory placeholders are tracked.

Secrets and local environment files are also excluded:

```text
.env
.venv/
```

---

## Development Roadmap

### Foundation

* [x] Project architecture
* [x] Python virtual environment
* [x] Git repository
* [x] `pyproject.toml`
* [x] Application configuration
* [x] Logging
* [x] pytest infrastructure

### Document Ingestion

* [x] Normalized `Document` model
* [x] TXT loader
* [x] PDF loader
* [x] Page-aware PDF metadata
* [x] DOCX loader
* [x] Unified document loader
* [x] Ingestion tests

### RAG Core

* [ ] Chunk model
* [ ] Character-based chunking
* [ ] Chunk overlap
* [ ] Metadata propagation
* [ ] Local embedding model
* [ ] Vector database
* [ ] Semantic search
* [ ] Local LLM integration
* [ ] Complete RAG pipeline
* [ ] Source citations

### Retrieval Improvements

* [ ] Hybrid search
* [ ] Reranking
* [ ] Context management
* [ ] Duplicate handling
* [ ] Retrieval benchmarking

### Evaluation

* [ ] Retrieval evaluation
* [ ] Answer evaluation
* [ ] Groundedness testing
* [ ] Citation accuracy
* [ ] Evaluation dataset
* [ ] Benchmark reporting

### Application Layer

* [ ] FastAPI backend
* [ ] REST API
* [ ] Interactive web interface
* [ ] File upload workflow
* [ ] Streaming responses

### AI Tooling

* [ ] MCP server
* [ ] MCP document search tools

### Production Engineering

* [ ] Expanded automated tests
* [ ] Docker
* [ ] CI pipeline
* [ ] Deployment
* [ ] Monitoring and observability

### Portfolio Presentation

* [ ] Final architecture diagram
* [ ] Retrieval benchmarks
* [ ] Evaluation results
* [ ] API documentation
* [ ] Screenshots
* [ ] Demo video
* [ ] Live deployment
* [ ] Final technical case study

---

## Planned Technology Stack

Current:

```text
Python
pypdf
python-docx
pytest
ReportLab (test fixtures)
```

Planned components will include technologies for:

```text
Local embeddings
Vector storage
BM25 / lexical search
Reranking
Local LLM inference
FastAPI
MCP
Docker
Frontend
Evaluation
CI/CD
Deployment
```

Specific technologies will be selected when each component is implemented rather than prematurely locking the project into a framework.

---

## Engineering Principles

NexusRAG follows several development principles:

**Understand before abstracting**

Core RAG components are implemented explicitly before adopting higher-level frameworks.

**Consistent interfaces**

Components expose predictable input and output contracts.

**Metadata is preserved**

Source information must survive ingestion, chunking, retrieval, and generation so answers can eventually provide reliable citations.

**Test behavior, not just execution**

Tests verify expected system behavior, edge cases, and metadata integrity.

**Local-first development**

Core functionality should work without requiring a paid LLM API.

**Incremental architecture**

Complex abstractions are introduced only when they provide a concrete engineering advantage.

---

## Current Pipeline

```text
                       NexusRAG

                  ┌─────────────────┐
                  │ User Documents  │
                  └────────┬────────┘
                           │
                ┌──────────┼──────────┐
                ▼          ▼          ▼
              PDF        DOCX        TXT
                │          │          │
                └──────────┼──────────┘
                           ▼
                  ┌─────────────────┐
                  │ Unified Loader  │
                  └────────┬────────┘
                           ▼
                  ┌─────────────────┐
                  │    Document     │
                  │                 │
                  │ ID              │
                  │ text            │
                  │ source          │
                  │ file type       │
                  │ metadata        │
                  └────────┬────────┘
                           │
                           ▼
                     Chunking
                       NEXT
```

---

## Project Goal

The final NexusRAG system will allow users to upload private documents, build a searchable knowledge base, and ask questions that produce answers grounded in retrieved evidence with traceable citations.

The project is being built as an **AI engineering portfolio project**, with emphasis not only on model usage but also on retrieval systems, software architecture, testing, APIs, deployment, evaluation, and production engineering.
