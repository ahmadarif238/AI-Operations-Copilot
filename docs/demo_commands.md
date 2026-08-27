# Demo Script & Commands

## Prerequisites
- Docker & Docker Compose installed
- Python 3.10+ (for local seeding tools)

## 1. Start System
```bash
cp .env.example .env
# Edit .env with your keys (or leave blank for test/mock modes)
docker-compose up --build -d
```

## 2. Seed Data
Open a new terminal:
```bash
# If running tools locally
pip install -r backend/requirements.txt
python tools/seed_db.py
python tools/generate_sops.py
```

## 3. Upload & Index Docs
```bash
curl -X POST "http://localhost:8000/api/v1/docs/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@docs/sample_sops/FIN_003_Expense_Reimbursement.pdf" \
  -F "department=Finance"
```

## 4. Ask a Question (RAG)
```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the meal limit?",
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  }'
```
**Expected Output:** JSON with `answer` containing "$50/day" and `sources` list.

## 5. Trigger Incident (Ops Monitor)
```bash
curl -X POST "http://localhost:8000/api/v1/log" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "ERROR",
    "message": "Critical failure in payment gateway",
    "meta": {"source": "payment-service"}
  }'
```
**Expected Output:** Status 202. Dashboard should show a new High severity ticket shortly.

## 6. Dashboard
Visit: [http://localhost:3000](http://localhost:3000)
- Check "Recent Incidents"
- Check "Pending Tickets" count

## 7. Metrics
Visit: [http://localhost:3001](http://localhost:3001) for Grafana (Login: admin/admin) -> Add Prometheus source `http://prometheus:9090`.
