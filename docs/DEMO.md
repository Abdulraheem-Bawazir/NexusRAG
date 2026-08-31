# NexusRAG Demo Guide

This guide describes a short portfolio demo that shows the strongest NexusRAG capabilities without spending too much time on setup details.

Target demo length:

```text
3 to 5 minutes
```

---

# Before Recording

Start Ollama and confirm the model exists:

```powershell
ollama list
```

Expected model:

```text
qwen3:4b
```

Start NexusRAG:

```powershell
python -m uvicorn app.main:app
```

or use Docker:

```powershell
docker compose up --build -d
```

Open:

```text
http://localhost:8000
```

---

# Demo Flow

## 1. Introduction

Suggested narration:

> NexusRAG is a local-first private-document Retrieval-Augmented Generation system that I built to explore the engineering behind production-style RAG rather than using a high-level framework to hide the pipeline.

Keep this section short.

---

# 2. Show the Interface

Show the main NexusRAG page.

Point out:

```text
document knowledge base
upload area
grounded query interface
system health indicator
```

Mention:

> The application supports PDF, DOCX, and TXT documents.

---

# 3. Upload a Document

Upload a document containing information that is easy to verify.

A CV is a good example because it contains:

```text
skills
education
projects
technologies
```

Wait until it appears in the indexed document list.

Explain:

> On upload, NexusRAG parses the file, normalizes its content, creates overlapping chunks, generates local MiniLM embeddings, and stores them in ChromaDB.

---

# 4. Ask a Semantic Question

Ask:

```text
What are the listed skills?
```

Show the generated answer.

Explain:

> The question is embedded locally and searched using both semantic retrieval and BM25 keyword retrieval.

---

# 5. Show the Citation

Point to:

```text
source PDF
page number
```

Explain:

> The model does not generate citation metadata itself. It returns evidence indexes, and NexusRAG maps those indexes back to retrieved chunks, which keeps citations traceable to actual document metadata.

---

# 6. Explain Hybrid Retrieval

Briefly show the conceptual architecture:

```text
Semantic Retrieval
        +
      BM25
        |
        v
Reciprocal Rank Fusion
```

Suggested narration:

> Semantic retrieval is strong for meaning, while BM25 is useful for exact names, codes, and identifiers. NexusRAG combines both rankings using Reciprocal Rank Fusion.

---

# 7. Show API Documentation

Open:

```text
http://localhost:8000/docs
```

Show:

```text
POST /api/v1/documents
GET /api/v1/documents
DELETE /api/v1/documents/{document_id}
POST /api/v1/query
GET /health
```

Explain:

> The frontend uses the same FastAPI application that can also be consumed programmatically.

---

# 8. Mention MCP

Show the MCP source folder or terminal.

Implemented tools:

```text
list_documents
search_documents
ask_documents
```

Suggested narration:

> NexusRAG also exposes the same application engine through MCP, so MCP-compatible AI clients can search and query the private knowledge base.

---

# 9. Show Evaluation

Run:

```powershell
python scripts\verify_retrieval_evaluation.py
```

Show:

```text
Cases: 4
Hit Rate@3: 1.0
Recall@3: 1.0
MRR: 1.0
```

Say explicitly:

> This is a small four-query verification benchmark, so I report these metrics only for that dataset rather than claiming general 100 percent accuracy.

This demonstrates good engineering judgment.

---

# 10. Show Tests

Run:

```powershell
pytest -q
```

Show:

```text
179 passed
```

Then:

```powershell
python -m ruff check .
```

Show:

```text
All checks passed!
```

---

# 11. Show Docker

Run:

```powershell
docker compose up -d
docker compose ps
```

Show the healthy container.

Explain:

> The application is containerized with persistent data storage and a Docker healthcheck. The local Ollama model remains on the host and the container connects to it.

---

# 12. Closing

Suggested closing statement:

> NexusRAG helped me move beyond RAG theory into the engineering required to build, test, evaluate, expose, and package a complete retrieval-augmented generation system.

---

# Demo Checklist

Before recording:

- [ ] Ollama running
- [ ] qwen3:4b installed
- [ ] NexusRAG starts successfully
- [ ] browser interface loads
- [ ] test PDF prepared
- [ ] upload works
- [ ] answer works
- [ ] citation appears
- [ ] page number appears
- [ ] Swagger works
- [ ] evaluation script works
- [ ] tests pass
- [ ] Docker works
- [ ] desktop notifications hidden
- [ ] no private information visible

---

# Suggested Recording Order

```text
1. UI
2. Upload
3. Question
4. Citation
5. Architecture explanation
6. Swagger
7. MCP
8. Evaluation
9. Tests
10. Docker
```

Do not spend the demo installing dependencies or waiting for models to download.

Prepare everything beforehand.

---

# Claims Safe to Use

These statements have been verified during development:

- NexusRAG supports PDF, DOCX, and TXT ingestion.
- Embeddings run locally using all-MiniLM-L6-v2.
- The embedding dimension is 384.
- ChromaDB provides persistent local vector storage.
- Retrieval combines semantic search and BM25.
- Reciprocal Rank Fusion combines rankings.
- Generation runs locally through Ollama using Qwen3 4B.
- Answers use structured output and citation validation.
- PDF page metadata can appear in citations.
- FastAPI exposes the RAG application through REST.
- NexusRAG exposes document functionality through MCP.
- The project includes Docker and Docker Compose.
- GitHub Actions runs automated quality checks.
- The current test suite contains 179 passing tests.
- A four-query retrieval verification set achieved Hit Rate@3 = 1.0, Recall@3 = 1.0, and MRR = 1.0.

---

# Claims to Avoid

Do not say:

```text
100% accurate
zero hallucinations
production proven
enterprise scale
best RAG system
perfect retrieval
```

unless future controlled benchmarks support those claims.

Prefer:

> The current four-query retrieval verification set achieved 1.0 Hit Rate@3, Recall@3, and MRR.

That is accurate and defensible.