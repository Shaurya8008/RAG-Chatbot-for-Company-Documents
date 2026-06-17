"""
Admin router — dashboard stats, audit logs, and system health.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, Document, ChatSession, ChatMessage, AuditLog, DocumentStatus, UserRole
from app.routers.auth import get_current_user
from app.services.ingestion import ingestion_service
from app.services.embeddings import embedding_service
from app.services.generation import generation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get admin dashboard statistics."""
    total_docs = db.query(Document).count()
    indexed_docs = db.query(Document).filter(Document.status == DocumentStatus.INDEXED).count()
    failed_docs = db.query(Document).filter(Document.status == DocumentStatus.FAILED).count()
    total_users = db.query(User).count()
    total_sessions = db.query(ChatSession).count()
    total_messages = db.query(ChatMessage).filter(ChatMessage.role == "user").count()

    # Collection stats
    collection_stats = ingestion_service.get_collection_stats()

    # Recent activity
    recent_queries = (
        db.query(AuditLog)
        .filter(AuditLog.action == "query")
        .order_by(AuditLog.timestamp.desc())
        .limit(10)
        .all()
    )

    return {
        "documents": {
            "total": total_docs,
            "indexed": indexed_docs,
            "failed": failed_docs,
            "pending": total_docs - indexed_docs - failed_docs,
        },
        "users": {
            "total": total_users,
        },
        "chat": {
            "total_sessions": total_sessions,
            "total_queries": total_messages,
        },
        "vector_store": collection_stats,
        "recent_queries": [
            {
                "query": log.details.get("query", "") if log.details else "",
                "confidence": log.details.get("confidence", "") if log.details else "",
                "timestamp": log.timestamp.isoformat() if log.timestamp else "",
            }
            for log in recent_queries
        ],
    }


@router.get("/audit-logs")
async def get_audit_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get recent audit logs."""
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "details": log.details,
            "timestamp": log.timestamp.isoformat() if log.timestamp else "",
        }
        for log in logs
    ]


@router.get("/health")
async def health_check():
    """System health check — Ollama models, ChromaDB, etc."""
    embed_ok = await embedding_service.health_check()
    llm_ok = await generation_service.health_check()
    collection_stats = ingestion_service.get_collection_stats()

    return {
        "status": "healthy" if (embed_ok and llm_ok) else "degraded",
        "services": {
            "ollama_embeddings": {
                "status": "ok" if embed_ok else "unavailable",
                "model": embedding_service.model,
            },
            "ollama_llm": {
                "status": "ok" if llm_ok else "unavailable",
                "model": generation_service.model,
            },
            "chromadb": {
                "status": "ok",
                **collection_stats,
            },
        },
    }
