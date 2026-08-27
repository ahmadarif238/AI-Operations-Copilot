from app.db.base import SessionLocal
from app.db.models import DocChunk, Document
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def inspect_chunks():
    db = SessionLocal()
    try:
        # Get latest document
        doc = db.query(Document).order_by(Document.uploaded_at.desc()).first()
        if not doc:
            print("No documents found.")
            return
            
        print(f"Inspecting chunks for Document: {doc.filename} (ID: {doc.id})")
        
        chunks = db.query(DocChunk).filter(DocChunk.doc_id == doc.id).order_by(DocChunk.chunk_index).all()
        print(f"Found {len(chunks)} chunks.")
        
        for i, chunk in enumerate(chunks):
            print(f"\n--- Chunk {i} ---")
            print(f"Length: {len(chunk.text)}")
            print(f"Preview: {chunk.text[:200]}...")
            print("-----------------")
            
    finally:
        db.close()

if __name__ == "__main__":
    inspect_chunks()
