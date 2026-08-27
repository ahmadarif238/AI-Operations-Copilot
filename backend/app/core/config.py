import os
from typing import List, Union
from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Operations Copilot"
    API_V1_STR: str = "/api/v1"
    
    # DATABASE
    DATABASE_URL: str = "postgresql://user:pass@localhost/db"
    
    # REDIS
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # SECURITY
    SECRET_KEY: str = "changethis"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 
    
    # VECTOR STORE
    VECTOR_STORE: str = "pinecone" # pinecone, weaviate, chroma
    PINECONE_API_KEY: str = ""
    PINECONE_ENV: str = "us-west1-gcp"
    PINECONE_INDEX_NAME: str = "ai-ops-v2"
    
    # LLM
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # INTEGRATIONS
    SLACK_WEBHOOK_URL: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""
    SMTP_URL: str = ""
    
    TEST_MODE: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

settings = Settings()
