# Changelog

All notable NexusRAG changes are documented here.

## v0.1.0

Initial portfolio release.

### RAG Core

- PDF, DOCX, and TXT ingestion
- Normalized document model
- Page-aware PDF metadata
- Configurable overlapping chunking
- Deterministic chunk IDs
- Local MiniLM embeddings
- Persistent ChromaDB vector storage
- Semantic retrieval
- BM25 lexical retrieval
- Reciprocal Rank Fusion
- Pluggable reranker interface

### Grounded Generation

- Local Qwen3 generation through Ollama
- Context construction
- Structured JSON output
- Citation validation
- PDF page citations
- Insufficient-evidence handling

### Evaluation

- Hit Rate@K
- Recall@K
- Mean Reciprocal Rank
- Citation precision
- Citation recall
- Citation F1
- Guardrail tests

Current four-query retrieval verification:

```text
Hit Rate@3: 1.0
Recall@3:   1.0
MRR:        1.0