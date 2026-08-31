# NexusRAG Engineering Case Study

## Project

**NexusRAG — Local-First Private Document RAG System**

---

# Problem

A basic document chatbot can often be assembled quickly by combining an LLM with a vector database.

However, production-style RAG requires more than a successful demo.

Important questions include:

- How are documents normalized?
- How are chunks identified?
- Is metadata preserved?
- How are duplicate vectors prevented?
- What happens when semantic retrieval misses an exact term?
- How are multiple retrieval strategies combined?
- Can the LLM cite only real evidence?
- What happens when evidence is insufficient?
- How can retrieval quality be measured?
- Can the system run locally without a paid LLM?
- Can it be tested without loading expensive AI components every time?
- Can it be packaged and deployed reproducibly?

NexusRAG was built to address those engineering concerns directly.

---

# Goals

The project goals were:

1. Build the RAG pipeline explicitly.
2. Keep core AI functionality local.
3. Preserve source metadata through the full pipeline.
4. Combine semantic and lexical retrieval.
5. Generate answers only from retrieved evidence.
6. Produce traceable citations.
7. Measure retrieval quality.
8. Expose functionality through REST and MCP.
9. Provide a usable frontend.
10. Package the system using Docker.
11. Maintain automated testing and CI.

---

# Document Processing

The first challenge was creating one downstream representation for multiple file types.

Supported formats:

```text
PDF
DOCX
TXT
```

Each loader normalizes its input into a `Document` model.

PDF ingestion remains page-aware.

That design decision became important later because page metadata could then appear inside final citations.

---

# Chunk Identity

Retrieval systems need stable chunk identity.

NexusRAG generates deterministic chunk IDs from:

```text
document ID
chunk index
chunk text
```

using SHA-256.

Benefits include:

- repeatable indexing
- duplicate-safe vector upserts
- stable retrieval references
- easier testing

---

# Local Embeddings

NexusRAG uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The model runs locally and produces 384-dimensional embeddings.

An embedding-provider abstraction prevents the RAG pipeline from depending directly on one implementation.

---

# Persistent Vector Storage

ChromaDB provides persistent local vector storage.

The vector-store layer supports:

```text
upsert
query
deletion
document deletion
collection clearing
metadata filters
persistence
```

---

# Retrieval Problem

Semantic search handles conceptual similarity well.

For example:

```text
Question:
Can employees work from home?
```

can retrieve text containing:

```text
Employees may work remotely...
```

However, semantic retrieval is not always the strongest strategy for exact identifiers.

Examples include:

```text
policy IDs
technical codes
error messages
product names
```

---

# Hybrid Retrieval Solution

NexusRAG combines:

```text
MiniLM semantic retrieval
+
BM25 lexical retrieval
```

using Reciprocal Rank Fusion.

RRF was chosen because Chroma distances and BM25 scores exist on different scales.

Instead of directly adding incompatible numbers, NexusRAG fuses result ranking positions.

---

# Grounding Problem

Retrieval alone does not guarantee the LLM will remain faithful to evidence.

The generation system therefore constructs numbered context blocks.

Example:

```text
[1]
Source: policy.pdf
Content:
Employees may work remotely...
```

The model is instructed to use only the supplied context.

---

# Structured Generation Solution

Instead of accepting arbitrary prose, NexusRAG asks the local LLM for structured JSON.

Example:

```json
{
  "answer": "Employees may work remotely up to three days per week.",
  "citations": [1],
  "insufficient_evidence": false
}
```

The application validates this data before building the final `RAGAnswer`.

---

# Citation Safety

The model does not get to invent arbitrary citation metadata.

It returns source indexes.

NexusRAG then maps those indexes back to evidence that actually exists in the retrieved context.

This design ensures citation metadata comes from the application rather than from model imagination.

---

# Local LLM

Generation uses:

```text
Ollama
qwen3:4b
```

The application includes defensive handling around Qwen thinking output so internal reasoning is not exposed as the final answer.

---

# Evaluation

NexusRAG implements retrieval evaluation metrics.

Current verification dataset:

```text
4 queries
```

Measured result:

```text
Hit Rate@3: 1.0
Recall@3:   1.0
MRR:        1.0
```

All expected chunks ranked first on the current verification set.

This result is deliberately presented as a small verification benchmark rather than as general system accuracy.

Citation precision, recall, and F1 utilities are also implemented.

---

# API Design

FastAPI exposes the RAG system through stable HTTP contracts.

Endpoints support:

```text
document upload
document listing
document deletion
grounded queries
health checking
```

Swagger/OpenAPI documentation is generated automatically.

---

# MCP Integration

NexusRAG also exposes document capabilities through Model Context Protocol.

Implemented tools:

```text
list_documents
search_documents
ask_documents
```

Both FastAPI and MCP use the same application engine.

This avoids maintaining separate RAG implementations for different interfaces.

---

# Testing Strategy

Heavy AI dependencies are separated from HTTP tests through dependency injection.

The API tests can replace the real engine with a lightweight fake engine.

This allows normal API behavior to be verified without repeatedly loading:

```text
MiniLM
ChromaDB
Ollama
```

Current verified test status:

```text
179 passed
```

Ruff status:

```text
All checks passed
```

---

# Production Engineering

NexusRAG includes:

```text
Dockerfile
Docker Compose
Docker healthcheck
persistent volume
environment-driven configuration
request logging
request IDs
GitHub Actions
automated Docker build
```

The containerized application was manually verified through the complete workflow:

```text
browser
->
Docker
->
FastAPI
->
retrieval
->
host Ollama
->
grounded answer
->
citation
```

---

# User Interface

The frontend provides a direct workflow for:

```text
upload
index
query
inspect citations
delete
```

It intentionally avoids a separate JavaScript framework so the portfolio project remains focused on AI engineering rather than frontend infrastructure.

---

# Engineering Lessons

## RAG is primarily a retrieval engineering problem

The LLM is only one part of the system.

Document representation, chunking, indexing, retrieval, metadata, evaluation, and evidence handling strongly affect reliability.

## Metadata must be preserved from the beginning

Reliable page citations are much easier when page information survives ingestion, chunking, indexing, and retrieval.

## Semantic search alone is not enough

Hybrid semantic + BM25 retrieval handles a wider variety of real queries.

## Model output should not be blindly trusted

Structured output and application-side validation reduce failure modes.

## Evaluation must be honest

A perfect result on four test cases is useful verification, but it is not equivalent to universal accuracy.

## Test architecture matters

Dependency injection allows application-level tests to stay fast even when the real system contains large AI dependencies.

---

# Current Limitations

NexusRAG currently does not include:

```text
OCR for scanned PDFs
learned cross-encoder reranking
large-scale evaluation dataset
formal generation accuracy benchmark
full multi-user authentication
cloud production deployment
```

These are intentionally documented rather than hidden.

---

# Outcome

NexusRAG evolved from a document parser into a complete local-first RAG application.

Final implemented path:

```text
Document
  ->
Chunk
  ->
Embedding
  ->
Vector Index
  ->
Semantic + BM25 Retrieval
  ->
RRF
  ->
Grounded Context
  ->
Local LLM
  ->
Validated Citation
  ->
FastAPI / MCP / Web UI
  ->
Docker / CI
```

The project demonstrates practical work across AI engineering, retrieval systems, backend architecture, testing, evaluation, tooling, and production engineering.