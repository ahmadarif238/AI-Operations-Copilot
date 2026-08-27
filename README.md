# AI Operations Copilot

An internal multi-agent operations assistant that answers SOP/policy questions, monitors logs, generates tickets, and produces weekly summaries.

## Features
- **RAG-based SOP Q&A**: Answers questions based on uploaded PDF/DOCX policies using Groq LLaMA 3.
- **Ops Monitoring**: Detects anomalies in logs and auto-creates tickets.
- **Agentic Workflow**: Uses LangGraph to orchestrate Retrieval, Monitoring, Ticketing, and Notification agents.
- **Weekly Summaries**: Generates reports on operational health.
- **Full Stack**: FastAPI Backend, React Frontend, PostgreSQL, Redis.

## Quick Start (Demo)

### Prerequisites
- Docker & Docker Compose
- API Keys (Groq, Pinecone - see `.env.example`)

### 1. Setup
```bash
# Clone repo
git clone <repo_url>
cd ai-ops-copilot

# Configure Environment
cp .env.example .env
# EDIT .env with your API keys! 
```

### 2. Run
```bash
docker-compose up --build
```
Access the dashboard at `http://localhost:3000`.
API Docs (Swagger) at `http://localhost:8000/docs`.

### 3. Seed Data
Open a new terminal:
```bash
# Generate dummy SOPs and Seed DB
python tools/seed_db.py
python tools/generate_sops.py
```

### 4. Index Docs & Demo
Use the "Docs Upload" page in the UI to upload the generated SOPs from `docs/sample_sops`.

## Architecture
See `docs/architecture.md` for details.
