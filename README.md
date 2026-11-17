# AI Operations Copilot
### Multi-Agent SOP Retrieval, Log Anomaly Monitoring & Incident Management

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-FF9900.svg)](https://langchain-ai.github.io/langgraph/)
[![React](https://img.shields.io/badge/Frontend-React_+_TypeScript-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Pinecone](https://img.shields.io/badge/Vector%20Store-Pinecone-000000.svg?logo=pinecone&logoColor=white)](https://www.pinecone.io/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Cache%20&%20Queue-Redis-DC382D.svg?logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Deployment-Docker_Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## System Overview

Internal DevOps and IT operations teams frequently face two parallel inefficiencies: fragmented access to internal Standard Operating Procedures (SOPs) buried across unstructured policy documents, and alert fatigue caused by manually correlating high-volume system logs with incident response protocols.

**AI Operations Copilot** is an enterprise multi-agent system orchestrated with **LangGraph**. It automates internal knowledge retrieval over vectorized operational documentation while continuously monitoring ingestion logs to detect anomalies, auto-generate tracked incident tickets in PostgreSQL, and synthesize weekly reliability reports.

---

## Multi-Agent Architecture

```mermaid
flowchart TD
    User["Operator / Engineer UI"] --> API["FastAPI Gateway"]
    SysLog["System Log Stream"] --> API
    
    API --> RedisQ[("Redis Task Queue")]
    API --> DB[("PostgreSQL Store")]
    
    subgraph MultiAgentCore ["LangGraph Multi-Agent Orchestration Layer"]
        Router["1. Query Router Agent\n(Classifies Query vs. Incident vs. Report)"]
        
        Router -->|Intent: Policy Query| RetrievalAgent["2. Retrieval Agent\n(Dense Search over SOPs in Pinecone)"]
        Router -->|Intent: Weekly Metrics| SummaryAgent["3. Reliability Summary Agent\n(Weekly Aggregation & Health Matrix)"]
        
        RedisQ --> MonitorAgent["4. Ops Monitor Agent\n(Anomaly Detection & Heuristic Filtering)"]
        MonitorAgent -->|Anomaly Detected| TicketAgent["5. Incident Ticket Agent\n(Structured Severity Assignment)"]
        TicketAgent --> NotifyAgent["6. Notification Agent\n(Alert Dispatch & Audit Logging)"]
    end
    
    RetrievalAgent --> VectorDB[("Pinecone Vector DB")]
    RetrievalAgent --> GroqLLM["Groq Llama 3 Inference"]
    TicketAgent --> DB
```

### Agent Roles

1. **Query Router Agent:** Evaluates natural language input to route execution paths between knowledge retrieval, active incident queries, and operational summaries.
2. **Retrieval Agent:** Decomposes SOP documentation (PDF / DOCX) into chunked embeddings within Pinecone and generates factual answers citing source sections.
3. **Ops Monitor Agent:** Evaluates incoming server and application log records against anomaly heuristics to detect error spikes, connection drops, and service degradations.
4. **Incident Ticket Agent:** Parses detected anomalies into structured incident tickets with severity levels (P1-P4) and writes them to PostgreSQL.
5. **Notification Agent:** Dispatches actionable notification payloads to configured communication webhooks.
6. **Weekly Summary Agent:** Compiles weekly Mean-Time-To-Acknowledge (MTTA), ticket volumes, and recurrence rates into an operational executive brief.

---

## Technical Stack

* **Backend Services:** FastAPI, Python 3.10, SQLAlchemy ORM, Pydantic data schemas.
* **Agentic Orchestration:** LangGraph state machine coordinating deterministic task dependencies.
* **Vector Indexing & RAG:** Pinecone serverless vector database paired with Groq Llama 3 inference.
* **Relational Storage & Queues:** PostgreSQL for ticket lifecycle and audit logs; Redis for background asynchronous task queuing.
* **Frontend Dashboard:** React 18, TypeScript, Vite, Tailwind CSS with real-time incident telemetry.

---

## Setup & Deployment

### 1. Repository Setup
```bash
git clone https://github.com/ahmadarif238/AI-Operations-Copilot.git
cd AI-Operations-Copilot
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Configure GROQ_API_KEY, PINECONE_API_KEY, and database credentials in .env
```

### 3. Full-Stack Docker Deployment
```bash
docker-compose up --build
```
* Client Dashboard: `http://localhost:3000`
* FastAPI Swagger Documentation: `http://localhost:8000/docs`

### 4. Database Seeding & SOP Document Indexing
In a separate terminal:
```bash
# Seed database schemas and synthetic log records
python tools/seed_db.py

# Generate and index sample SOP operational documents
python tools/generate_sops.py
```

---

## Author & Academic Context

Engineered by **Arif Ahmad Khan** as an implementation of multi-agent state machines applied to internal DevOps reliability engineering and automated log intelligence.

Released under the [MIT License](LICENSE).
