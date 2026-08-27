from sqlalchemy.orm import Session
from app.db.models import Log, Ticket, Document, DocChunk, User, Notification
from app.api.v1.schemas import LogCreate, TicketCreate
import uuid

def create_log(db: Session, log_in: LogCreate):
    db_log = Log(**log_in.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def create_ticket(db: Session, ticket_in: TicketCreate, created_by: uuid.UUID = None):
    db_ticket = Ticket(
        **ticket_in.model_dump(),
        created_by=created_by,
        status="open"
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def get_ticket(db: Session, ticket_id: uuid.UUID):
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()

def get_open_tickets(db: Session):
    return db.query(Ticket).filter(Ticket.status == "open").all()

def create_document(db: Session, filename: str, department: str = None, category: str = None):
    db_doc = Document(filename=filename, department=department, category=category)
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def create_doc_chunks(db: Session, doc_id: uuid.UUID, chunks_data: list):
    chunks = []
    for data in chunks_data:
        chunk = DocChunk(
            doc_id=doc_id,
            chunk_index=data.get("index"),
            text=data.get("text"),
            metadata_=data.get("metadata")
            # embedding vector usually goes to Pinecone, but we can store here too if local
        )
        chunks.append(chunk)
    db.add_all(chunks)
    db.commit()
    return len(chunks)

def get_logs_by_range(db: Session, start_time, end_time):
    return db.query(Log).filter(Log.timestamp >= start_time, Log.timestamp <= end_time).all()

def search_doc_chunks(db: Session, query_text: str, limit: int = 5):
    # Improved keyword search: split query into terms
    from sqlalchemy import or_
    
    terms = query_text.split()
    # Filter out small words
    terms = [t for t in terms if len(t) > 3]
    
    if not terms:
        terms = [query_text]
        
    conditions = [DocChunk.text.ilike(f"%{term}%") for term in terms]
    
    return db.query(DocChunk).filter(or_(*conditions)).limit(limit).all()

def get_dashboard_stats(db: Session):
    from datetime import datetime, timedelta
    
    # 1. Pending Tickets (Open + In Progress) - for simplicity just Open
    pending_count = db.query(Ticket).filter(Ticket.status.in_(["open", "in_progress"])).count()
    
    # 2. Resolved Today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    resolved_count = db.query(Ticket).filter(
        Ticket.status == "resolved",
        Ticket.updated_at >= today_start
    ).count()
    
    # 3. Recent Tickets
    recent_tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).limit(5).all()
    
    return {
        "pending_tickets": pending_count,
        "resolved_today": resolved_count,
        "recent_tickets": recent_tickets
    }
