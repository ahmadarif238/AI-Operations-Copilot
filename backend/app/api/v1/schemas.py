from pydantic import BaseModel, UUID4, EmailStr, Field
from typing import List, Optional, Any, Dict
from uuid import UUID
from datetime import datetime

# --- Common ---
class APIResponse(BaseModel):
    success: bool = True
    message: str = "Success"
    data: Optional[Any] = None

# --- Logs ---
class LogCreate(BaseModel):
    type: str # INFO, ERROR, WARN
    message: str
    meta: Optional[Dict[str, Any]] = None

class LogResponse(BaseModel):
    id: UUID4
    job_id: str

# --- Docs ---
class DocSchema(BaseModel):
    id: UUID4
    filename: str
    department: Optional[str] = None
    category: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True

class DocUploadResponse(BaseModel):
    file_ids: List[UUID4]
    chunk_counts: Dict[str, int]

# --- Tickets ---
class TicketCreate(BaseModel):
    title: str
    description: str
    severity: str = "medium"
    assigned_to: Optional[UUID4] = None

class TicketResponse(BaseModel):
    id: UUID4
    title: str
    status: str
    created_at: datetime
    url: Optional[str] = None

    class Config:
        from_attributes = True

# --- Ask/Query ---
class AskRequest(BaseModel):
    query: str
    user_id: Optional[UUID] = None
    channel: Optional[str] = None # slack, web, etc.

class Source(BaseModel):
    filename: str
    page: Optional[int] = None
    chunk_id: Optional[UUID4] = None
    score: Optional[float] = None
    text: Optional[str] = None

class AskResponse(BaseModel):
    answer: str
    sources: List[Source]
    ticket_suggestion: bool = False
    ticket_id: Optional[UUID4] = None
    confidence: Optional[float] = None

# --- Notifications ---
class NotificationSend(BaseModel):
    target: str
    channel: str
    message: str
    urgency: str = "normal"

# --- Summaries ---
class WeeklySummary(BaseModel):
    start_date: str
    end_date: str
    total_logs_analyzed: int
    tickets_created: int
    top_issues: List[str]
    summary_text: str
    pdf_url: Optional[str] = None

class DashboardStats(BaseModel):
    pending_tickets: int
    resolved_today: int
    avg_response_time: str = "45m" # Hardcoded for now
    recent_tickets: List[TicketResponse]
