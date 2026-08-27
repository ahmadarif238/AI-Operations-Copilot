from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging import logger

class Retriever:
    def __init__(self):
        pass

    async def retrieve(self, query: str, top_k: int = 5, filters: Dict = None) -> List[Dict]:
        """
        Search vector store for relevant chunks.
        """
        logger.info(f"Retrieving for query: {query}")
        
        # Embed Query
        query_vector = await self._get_embedding(query)
        
        if settings.VECTOR_STORE == "pinecone" and settings.PINECONE_API_KEY:
            try:
                from pinecone import Pinecone
                
                pc = Pinecone(api_key=settings.PINECONE_API_KEY)
                index_name = settings.PINECONE_INDEX_NAME or "ai-ops"
                index = pc.Index(index_name)
                
                search_results = index.query(
                    vector=query_vector,
                    top_k=top_k,
                    include_metadata=True
                )
                
                results = []
                for match in search_results["matches"]:
                    # Flatten to match Source(BaseModel) schema
                    # Schema expects: filename, page, chunk_id, score, text
                    md = match.get("metadata", {})
                    results.append({
                        "filename": md.get("source", "unknown"),
                        "text": md.get("text", ""), 
                        "score": match["score"],
                        "chunk_id": None, # Pinecone ID is string, schema expects UUID, skip for now or fix schema
                        "page": md.get("page")
                    })
                return results
                
            except Exception as e:
                logger.error(f"Pinecone Search Error: {e}")
                # Fallback to DB
                return await self._fallback_db_search(query, top_k)
        else:
            return await self._fallback_db_search(query, top_k)

    async def _fallback_db_search(self, query, top_k):
        # Fallback: Simple Keyword Search in Postgres
        from app.db.base import SessionLocal
        from app.db import crud
        
        db = SessionLocal()
        try:
            chunks = crud.search_doc_chunks(db, query, limit=top_k)
            chunks = crud.search_doc_chunks(db, query, limit=top_k)
            results = []
            for chunk in chunks:
                md = chunk.metadata_ or {}
                results.append({
                    "filename": md.get("source", "unknown_db_source"), 
                    "text": chunk.text,
                    "score": 0.5, 
                    "page": md.get("page"),
                    "chunk_id": chunk.id # UUID from DB
                })
            return results
        finally:
            db.close()

    async def _get_embedding(self, text: str) -> List[float]:
        try:
            from sentence_transformers import SentenceTransformer
            if not hasattr(self, "embedding_model"):
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            return self.embedding_model.encode(text).tolist()
        except ImportError:
             return [0.1] * 384

retriever = Retriever()
