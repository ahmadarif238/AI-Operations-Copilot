from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, Enum, Uuid, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Log(Base):
    __tablename__ = "logs"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    type = Column(String, nullable=False) # INFO, ERROR, WARN
    message = Column(Text, nullable=False)
    meta = Column(JSON, nullable=True)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="open", index=True) # open, in_progress, resolved
    severity = Column(String, default="medium") # low, medium, high, critical
    created_by = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_to = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target = Column(String, nullable=False) # email or slack channel id
    channel = Column(String, nullable=False) # slack, email, whatsapp
    message = Column(Text, nullable=False)
    status = Column(String, default="pending") # pending, sent, failed
    sent_at = Column(DateTime(timezone=True), nullable=True)
    meta = Column(JSON, nullable=True)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    department = Column(String, nullable=True, index=True)
    category = Column(String, nullable=True)
    uploaded_by = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    metadata_ = Column("metadata", JSON, nullable=True)
    
    chunks = relationship("DocChunk", back_populates="document", cascade="all, delete-orphan")

class DocChunk(Base):
    __tablename__ = "doc_chunks"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_id = Column(Uuid(as_uuid=True), ForeignKey("documents.id"))
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    embedding_vector = Column(JSON, nullable=True) # Storing vector here optionally, mostly in Pinecone
    metadata_ = Column("metadata", JSON, nullable=True)
    
    document = relationship("Document", back_populates="chunks")
