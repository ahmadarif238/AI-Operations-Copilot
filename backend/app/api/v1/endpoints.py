from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.db.base import get_db
from app.api.v1 import schemas
from app.db import crud
from app.rag import indexer
from app.core.logging import logger
from app.agents.langgraph_graph import app_graph

router = APIRouter()

@router.get("/dashboard", response_model=schemas.DashboardStats)
async def get_dashboard(db: Session = Depends(get_db)):
    stats = crud.get_dashboard_stats(db)
    return {
        "pending_tickets": stats["pending_tickets"],
        "resolved_today": stats["resolved_today"],
        "avg_response_time": "45m",
        "recent_tickets": stats["recent_tickets"]
    }

@router.post("/ask", response_model=schemas.AskResponse)
async def ask_question(request: schemas.AskRequest, db: Session = Depends(get_db)):
    """
    RAG + Agents query interface.
    """
    logger.info(f"Received query: {request.query}")
    
    # LangGraph execution
    inputs = {"query": request.query, "user_id": str(request.user_id), "next": None}
    result = await app_graph.ainvoke(inputs)
    
    return schemas.AskResponse(
        answer=result.get("answer", "Processed by Ops Copilot"),
        sources=result.get("sources", []),
        ticket_suggestion=True if result.get("ticket_id") else False,
        ticket_id=result.get("ticket_id"),
        confidence=1.0 # Placeholder
    )

@router.post("/log", status_code=202)
async def receive_log(
    log_in: schemas.LogCreate, 
    db: Session = Depends(get_db)
):
    """
    Receive logs and trigger monitoring agent via Redis Queue.
    """
    db_log = crud.create_log(db, log_in)
    
    # Enqueue Job
    # Enqueue Job
    try:
        from redis import Redis
        from rq import Queue
        from app.core.config import settings
        from app.worker import process_log_job
        
        # In prod, reuse connection
        redis_conn = Redis.from_url(settings.REDIS_URL or 'redis://localhost:6379/0')
        # Check connection
        redis_conn.ping()
        q = Queue(connection=redis_conn)
        
        # Enqueue the processing function with data
        job = q.enqueue(process_log_job, log_in.model_dump())
        job_id = job.id
        status = "accepted"
    except Exception as e:
        logger.error(f"Redis/RQ Error: {e}")
        job_id = "queued_db_only"
        status = "accepted_db_only"
    
    return {"status": status, "log_id": db_log.id, "job_id": job_id}

@router.post("/docs/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    department: str = Form(None),
    category: str = Form(None),
    uploaded_by: uuid.UUID = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload and index SOPs.
    """
    results = []
    for file in files:
        # Save file to disk logic
        temp_dir = "temp_uploads"
        import os
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            import shutil
            shutil.copyfileobj(file.file, buffer)
            
        doc = crud.create_document(db, file.filename, department, category)
        
        # Async indexing trigger
        # We need to pass the file PATH, not the file object, because file object might be closed
        # indexer.process_file is async, so we use app_graph approach or simple await if we want it synchronous here (blocking)
        # But for upload speed, better async.
        # Since we are inside an async route, we can just await it directly for simplicity to ensure it's done for the user demo.
        await indexer.indexer.process_file(file_path, doc.id, db, file.filename)
        
        results.append(doc.id)

    return {"file_ids": results, "chunk_counts": {f.filename: 5 for f in files}} # mock counts

@router.post("/tickets/create", response_model=schemas.TicketResponse)
async def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    db_ticket = crud.create_ticket(db, ticket)
    return {
        "id": db_ticket.id,
        "title": db_ticket.title,
        "status": db_ticket.status,
        "created_at": db_ticket.created_at,
        "url": f"/tickets/{db_ticket.id}"
    }

@router.post("/notifications/send")
async def send_notification(notification: schemas.NotificationSend):
    # Call NotificationAgent logic
    logger.info(f"Sending notification to {notification.target}")
    return {"status": "queued"}

@router.get("/summaries/weekly", response_model=schemas.WeeklySummary)
async def get_weekly_summary(start: str = None, end: str = None, db: Session = Depends(get_db)):
    # Call WeeklySummaryAgent via Graph
    inputs = {"query": "Generate weekly summary", "user_id": "system", "next": None}
    result = await app_graph.ainvoke(inputs)
    
    stats = result.get("summary_stats", {})
    
    return schemas.WeeklySummary(
        start_date=stats.get("start_date", start or "2023-01-01"),
        end_date=stats.get("end_date", end or "2023-01-07"),
        total_logs_analyzed=stats.get("total_logs_analyzed", 0),
        tickets_created=stats.get("tickets_created", 0),
        top_issues=stats.get("top_issues", []),
        summary_text=result.get("answer", "No summary generated."),
        pdf_url=None
    )
