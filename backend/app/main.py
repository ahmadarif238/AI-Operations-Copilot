from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up AI Operations Copilot API...")
    # Nothing previously created the tables (app/db/migrations/ is empty), so
    # every DB-backed endpoint failed with "no such table" on a fresh deploy.
    from app.db.base import init_db, DATABASE_URL, USING_FALLBACK
    init_db()
    logger.info(
        f"Database ready: {DATABASE_URL.split('://')[0]}"
        f"{' (local fallback)' if USING_FALLBACK else ''}"
    )

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

# Import and include routers here later
from app.api.v1.endpoints import router as api_router
app.include_router(api_router, prefix=settings.API_V1_STR)
