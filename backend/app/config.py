"""
Configuration settings for the RAG Chatbot backend.
Loaded from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_llm_model: str = "llama3.2"
    ollama_embed_model: str = "nomic-embed-text"

    # ChromaDB
    chroma_persist_dir: str = str(BASE_DIR / "data" / "chroma_db")
    chroma_collection_name: str = "hr_documents"

    # File storage
    upload_dir: str = str(BASE_DIR / "data" / "uploads")
    sample_data_dir: str = str(BASE_DIR.parent / "sample_data")

    # Database
    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'rag_assistant.db'}"

    # Auth
    secret_key: str = "change-this-to-a-random-secret-key-in-production"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Retrieval
    retrieval_top_k: int = 15
    rerank_top_k: int = 5
    chunk_size: int = 512
    chunk_overlap: int = 50

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# Ensure directories exist
os.makedirs(settings.chroma_persist_dir, exist_ok=True)
os.makedirs(settings.upload_dir, exist_ok=True)
