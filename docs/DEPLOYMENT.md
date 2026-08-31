# NexusRAG Deployment Guide

## Deployment Model

NexusRAG is designed as a local-first application.

The application container includes:

```text
FastAPI
Web UI
Document ingestion
Chunking
MiniLM embeddings
ChromaDB integration
Hybrid retrieval
Grounded generation integration
MCP components
```

The local LLM is provided separately by Ollama.

Current model:

```text
qwen3:4b
```

Architecture:

```text
Browser
   |
   v
NexusRAG Docker Container
   |
   +--> FastAPI
   +--> ChromaDB
   +--> MiniLM
   |
   v
Host Ollama
   |
   v
Qwen3 4B
```

---

## Local Docker Deployment

Make sure Ollama is running:

```bash
ollama list
```

Expected model:

```text
qwen3:4b
```

Start NexusRAG:

```bash
docker compose up --build -d
```

Check status:

```bash
docker compose ps
```

Expected:

```text
nexusrag-api ... Up ... (healthy)
```

Open:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

Health endpoint:

```text
http://localhost:8000/health
```

Stop:

```bash
docker compose down
```

Do not use `docker compose down -v` unless the persistent NexusRAG volume should also be deleted.

---

## GitHub Container Registry

Release tags trigger the GitHub Actions release workflow.

Example:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The workflow builds NexusRAG and publishes the Docker image to:

```text
ghcr.io/<owner>/<repository>
```

Example release tags include:

```text
0.1.0
0.1
latest
```

---

## Running a Published Image

Pull the image:

```bash
docker pull ghcr.io/<owner>/<repository>:0.1.0
```

Run it:

```bash
docker run -d \
  --name nexusrag-api \
  --add-host=host.docker.internal:host-gateway \
  -p 8000:8000 \
  -e NEXUSRAG_OLLAMA_MODEL=qwen3:4b \
  -e NEXUSRAG_OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e NEXUSRAG_OLLAMA_TIMEOUT=300 \
  -e NEXUSRAG_VECTOR_STORE_DIR=/app/data/vector_store \
  -v nexusrag_data:/app/data \
  ghcr.io/<owner>/<repository>:0.1.0
```

Then open:

```text
http://localhost:8000
```

---

## Environment Variables

NexusRAG supports:

```text
NEXUSRAG_OLLAMA_MODEL
NEXUSRAG_OLLAMA_BASE_URL
NEXUSRAG_OLLAMA_TIMEOUT
NEXUSRAG_VECTOR_STORE_DIR
NEXUSRAG_LOG_LEVEL
```

See:

```text
.env.example
```

---

## Persistent Data

Docker stores NexusRAG data inside the named volume:

```text
nexusrag_data
```

This prevents indexed data from disappearing every time the application container is restarted.

---

## Health Checking

The Docker image includes a health check against:

```text
GET /health
```

A successful container should eventually report:

```text
healthy
```

using:

```bash
docker compose ps
```

---

## Ollama Requirement

The production container does not bundle the Qwen model.

This is intentional.

Bundling a multi-gigabyte language model inside the application image would make image distribution unnecessarily large and couple the application lifecycle to one specific LLM binary.

Instead:

```text
NexusRAG container
      |
      v
Ollama HTTP API
      |
      v
Local model
```

---

## Public Cloud Deployment

The current system is optimized for local-first execution.

A public deployment would require infrastructure capable of running or reaching an Ollama-compatible LLM service.

No free always-on public GPU deployment is claimed by this project.

Possible future deployment architectures include:

```text
Cloud VM + Ollama
Managed GPU inference
Remote Ollama-compatible service
CPU-only smaller language model
```

These remain future deployment options rather than current project claims.