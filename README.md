# NexusRAG

NexusRAG is a production-style private-document AI knowledge assistant built to explore the engineering behind modern Retrieval-Augmented Generation systems.

The goal is to build the important RAG components from the ground up before introducing higher-level frameworks.

## Planned Capabilities

- PDF, DOCX, and TXT document ingestion
- Document normalization
- Chunking
- Local embeddings
- Vector search
- Semantic retrieval
- Hybrid search
- Reranking
- Local LLM integration
- Grounded answers with citations
- RAG evaluation
- FastAPI backend
- Web interface
- MCP integration
- Automated testing
- Docker
- Deployment

## Current Status

Phase 1 — Project foundation completed.

## Tech Stack

Current:

- Python 3.11
- PyPDF
- python-docx
- pytest

More components will be added incrementally as the system grows.

## Project Structure

```text
NexusRAG/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   └── rag/
├── data/
│   ├── raw/
│   └── processed/
├── scripts/
├── tests/
├── README.md
├── pyproject.toml
└── .gitignore