"""
RAG Chatbot Backend — FastAPI Application Entry Point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import auth, chat, documents, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("🚀 Starting RAG Chatbot Backend...")
    init_db()
    logger.info("✅ Database initialized")
    logger.info(f"📦 Ollama LLM model: {settings.ollama_llm_model}")
    logger.info(f"📦 Ollama embed model: {settings.ollama_embed_model}")
    logger.info(f"📦 ChromaDB path: {settings.chroma_persist_dir}")
    yield
    logger.info("👋 Shutting down RAG Chatbot Backend")


app = FastAPI(
    title="RAG Chatbot API",
    description="Premium RAG Chatbot for Company Documents — Internal Knowledge Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
origins = [origin.strip() for origin in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {
        "name": "RAG Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
