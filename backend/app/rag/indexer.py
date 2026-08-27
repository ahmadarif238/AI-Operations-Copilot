import os
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.db import crud
import uuid

# Mock imports for now if libraries aren't installed in this environment, 
# but in Docker they will be.
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
except ImportError:
    # Fallback for when libraries aren't installed (e.g. in test env without heavy deps)
    class RecursiveCharacterTextSplitter:
        def __init__(self, chunk_size, chunk_overlap): pass
        def split_text(self, text): return [text]
        
    class PyPDFLoader:
        def __init__(self, path): pass
        def load(self): return []
        
    class Docx2txtLoader:
        def __init__(self, path): pass
        def load(self): return []
    class TextLoader: pass

class Indexer:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100
        )

    async def process_file(self, file_path: str, doc_id: uuid.UUID, db: Session, original_filename: str):
        """
        Reads file, chunks it, embeds it, and stores in Vector DB + PG.
        """
        logger.info(f"Indexing file: {file_path}")
        
        # 1. Load Text
        text = self._load_file(file_path)
        
        # 2. Chunk
        chunks = self.text_splitter.split_text(text)
        logger.info(f"Created {len(chunks)} chunks for {original_filename}")
        
        # 3. Store in PG (DocChunks)
        chunk_data = []
        vectors = [] # For pinecone
        
        for i, chunk_text in enumerate(chunks):
            # Embed chunk (Mock or Real)
            vector = await self._get_embedding(chunk_text)
            
            chunk_data.append({
                "index": i,
                "text": chunk_text,
                "metadata": {"source": original_filename, "doc_id": str(doc_id)}
            })
            
            vectors.append({
                "id": f"{doc_id}_{i}",
                "values": vector,
                "metadata": {"text": chunk_text, "source": original_filename}
            })
            
        crud.create_doc_chunks(db, doc_id, chunk_data)
        
        # 4. Upsert to Vector Store
        await self._upsert_vectors(vectors)
        
        return len(chunks)

    def _load_file(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == ".pdf":
                from pydantic import ValidationError
                try:
                    import pypdf
                    reader = pypdf.PdfReader(file_path)
                    text = ""
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                    
                    if not text.strip():
                        logger.warning(f"PDF {file_path} extracted to empty string. Is it an image scan?")
                        return "Error: Could not extract text from PDF (it might be an image)."
                        
                    return text
                except Exception as e:
                     logger.error(f"pypdf error: {e}")
                     return ""

            elif ext == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            elif ext == ".docx":
                # Only use loader if absolutely needed, or maybe simple python-docx
                loader = Docx2txtLoader(file_path)
                docs = loader.load()
                return "\n".join([d.page_content for d in docs])
            else:
                return "Unsupported file type."
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            return ""

    async def _get_embedding(self, text: str) -> List[float]:
        try:
            from sentence_transformers import SentenceTransformer
            # Load model (singleton pattern ideally, but here simple)
            if not hasattr(self, "embedding_model"):
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Encode returns numpy array, convert to list
            embedding = self.embedding_model.encode(text).tolist()
            return embedding
        except ImportError:
            logger.error("SentenceTransformers not installed. Returning mock embedding.")
            return [0.1] * 384 # MiniLM dimension is 384

    async def _upsert_vectors(self, vectors):
        if settings.VECTOR_STORE == "pinecone" and settings.PINECONE_API_KEY:
            try:
                from pinecone import Pinecone
                
                pc = Pinecone(api_key=settings.PINECONE_API_KEY)
                index_name = settings.PINECONE_INDEX_NAME or "ai-ops" # Capitalization fix
                
                # Create index if not exists (simplified check)
                # In prod, checking list_indexes is better
                
                index = pc.Index(index_name)
                
                # Upsert
                # vectors is a list of dicts: {id, values, metadata}
                # Pinecone expects (id, values, metadata) tuples or dicts
                
                conn_vectors = []
                for v in vectors:
                     conn_vectors.append((v["id"], v["values"], v["metadata"]))
                
                index.upsert(vectors=conn_vectors)
                logger.info(f"Upserted {len(vectors)} chunks to Pinecone index {index_name}")
                
            except Exception as e:
                logger.error(f"Pinecone Upsert Error: {e}")
        else:
            logger.info(f"Mocking vector upsert for {len(vectors)} vectors")

indexer = Indexer()
