# NexusRAG Architecture

## Overview

NexusRAG separates document processing, retrieval, generation, evaluation, and application concerns into independent components.

The system is intentionally designed so that major AI infrastructure choices can be replaced without rewriting the full application.

---

# End-to-End Flow

```text
User Document
     |
     v
PDF / DOCX / TXT Loader
     |
     v
Normalized Document
     |
     v
DocumentChunker
     |
     v
Chunk
     |
     +------------------------------+
     |                              |
     v                              v
Sentence Transformer             BM25
     |                              |
     v                              |
EmbeddedChunk                       |
     |                              |
     v                              |
ChromaDB                            |
     |                              |
     v                              |
SemanticRetriever                   |
     |                              |
     +---------------+--------------+
                     |
                     v
              HybridRetriever
                     |
                     v
            Reciprocal Rank Fusion
                     |
                     v
                 Reranker
                     |
                     v
            Retrieved Evidence
                     |
                     v
               ContextBuilder
                     |
                     v
              Grounded Prompt
                     |
                     v
              Ollama / Qwen3
                     |
                     v
            Structured JSON Output
                     |
                     v
             Citation Validation
                     |
                     v
                RAGAnswer
                     |
       +-------------+--------------+
       |             |              |
       v             v              v
    FastAPI          MCP          Web UI
```

---

# Layers

## 1. Document Layer

Supported formats:

```text
PDF
DOCX
TXT
```

Each source is normalized into the internal `Document` model.

Important fields include:

```text
id
text
source
file_type
metadata
```

PDF metadata can include page information for later citation generation.

---

## 2. Chunking Layer

Documents are transformed into `Chunk` objects.

Important properties:

```text
chunk ID
document ID
chunk index
text
source
file type
metadata
```

Chunk IDs are deterministic.

This provides stable identity across repeated ingestion runs.

---

## 3. Embedding Layer

The embedding architecture uses an `EmbeddingProvider` abstraction.

Current provider:

```text
SentenceTransformerEmbeddingProvider
```

Current model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Dimension:

```text
384
```

The layer supports both individual and batch embedding.

---

## 4. Vector Storage

Current vector database:

```text
ChromaDB
```

The vector store handles:

```text
upsert
query
count
delete chunk
delete document
clear collection
metadata filters
persistence
```

---

# Retrieval Architecture

NexusRAG uses two retrieval strategies.

## Semantic Retrieval

```text
Question
   |
   v
Query Embedding
   |
   v
ChromaDB
   |
   v
Distance-Ranked Results
```

Semantic retrieval handles meaning even when query wording differs from document wording.

## Lexical Retrieval

```text
Question
   |
   v
Tokenization
   |
   v
BM25
   |
   v
Keyword-Ranked Results
```

BM25 improves exact-term retrieval.

---

# Hybrid Fusion

Semantic and BM25 rankings are combined using Reciprocal Rank Fusion.

```text
semantic ranking
       |
       +------+
              |
              v
             RRF
              ^
              |
       +------+
       |
BM25 ranking
```

RRF avoids directly comparing incompatible raw score scales.

---

# Reranking

The architecture exposes a reranker protocol.

Current implementation:

```text
NoOpReranker
```

This keeps the retrieval pipeline extensible without falsely claiming a trained reranking model.

---

# Generation Architecture

The generation pipeline is:

```text
retrieved results
      |
      v
ContextBuilder
      |
      v
numbered evidence
      |
      v
grounded prompt
      |
      v
LLMProvider
      |
      v
structured response
      |
      v
validation
```

Current LLM provider:

```text
OllamaLLMProvider
```

Current local model:

```text
qwen3:4b
```

Thinking output is suppressed defensively before returning application output.

---

# Structured Output

The model is asked to return JSON:

```json
{
  "answer": "Evidence-supported answer",
  "citations": [1],
  "insufficient_evidence": false
}
```

The generation service validates:

```text
JSON structure
answer type
citation list type
citation index type
citation availability
insufficient_evidence type
required citations
```

Invalid model output is rejected.

---

# Citation Architecture

`ContextBuilder` assigns evidence numbers.

For example:

```text
[1]
Source: handbook.pdf
Metadata: page 14
Content:
...
```

If the model cites `[1]`, the application maps that number back to a `SourceCitation`.

The result preserves:

```text
chunk ID
document ID
source
file type
metadata
```

This avoids exposing unverified arbitrary source names generated by the model.

---

# Application Service

`NexusRAGEngine` coordinates the main application workflow.

Responsibilities include:

```text
ingestion
chunking
embedding
vector indexing
retrieval refresh
search
grounded question answering
document deletion
```

This keeps FastAPI and MCP adapters from containing core RAG logic.

---

# FastAPI Layer

FastAPI exposes:

```text
GET /health

POST /api/v1/documents
GET /api/v1/documents
DELETE /api/v1/documents/{document_id}

POST /api/v1/query
```

The API layer converts application models into HTTP response schemas.

---

# MCP Layer

The MCP server exposes:

```text
list_documents
search_documents
ask_documents
```

MCP uses the same application service as FastAPI.

Conceptually:

```text
            NexusRAGEngine
             /          \
            /            \
       FastAPI            MCP
```

This prevents duplicate AI logic.

---

# Web Layer

The browser interface is intentionally lightweight.

Stack:

```text
HTML
CSS
JavaScript
```

It communicates with the same FastAPI REST endpoints.

No separate frontend build system is required.

---

# Evaluation Layer

Retrieval metrics:

```text
Hit Rate@K
Recall@K
MRR
```

Citation metrics:

```text
Precision
Recall
F1
```

Guardrail checks validate both supported and unsupported question behavior.

---

# Production Layer

Docker packages:

```text
application
Python runtime
dependencies
FastAPI server
web assets
```

Ollama remains on the host machine and is accessed from Docker through:

```text
host.docker.internal
```

Persistent RAG data is stored using Docker volumes.

---

# Observability

The request middleware adds:

```text
X-Request-ID
```

and logs:

```text
request ID
method
path
status
duration
```

This allows individual API requests to be traced.

---

# CI Architecture

GitHub Actions performs:

```text
checkout
   |
   v
Python setup
   |
   v
dependency installation
   |
   +--> Ruff
   |
   +--> pytest

separate Docker job
   |
   v
docker build
```

---

# Design Decisions

## Explicit RAG components

Core RAG logic is implemented directly to keep important engineering decisions visible.

## Local AI stack

The primary development path avoids paid inference APIs.

## Dependency injection

FastAPI tests can replace the heavy RAG engine with test doubles.

This prevents normal API tests from loading MiniLM, Chroma, and Ollama.

## Typed models

Document, chunk, retrieval, answer, and citation boundaries use typed Python models.

## Deterministic indexing

Stable chunk IDs support repeatable and duplicate-safe ingestion.

## Structured generation

The model returns machine-readable output that the application validates before exposing it.

---

# Extension Points

The architecture is prepared for future additions such as:

```text
OCR
cross-encoder reranking
alternative embedding models
alternative vector stores
external metadata persistence
streaming generation
authentication
multi-user knowledge bases
larger evaluation datasets
cloud deployment
```

These remain extensions rather than current claims.