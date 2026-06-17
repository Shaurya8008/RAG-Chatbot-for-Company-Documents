"""
Document management router — upload, ingest, list, and delete documents.
"""

import os
import logging
import shutil
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User, Document, DocumentStatus, UserRole
from app.routers.auth import get_current_user
from app.services.ingestion import ingestion_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "md", "html"}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    department: str = Form("HR"),
    permission_level: str = Form("all_employees"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Upload and ingest a document."""
    # Check file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Save file
    file_path = os.path.join(settings.upload_dir, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Ingest
    doc_title = title or file.filename.rsplit(".", 1)[0].replace("_", " ").title()
    try:
        doc = await ingestion_service.ingest_document(
            db=db,
            file_path=file_path,
            title=doc_title,
            department=department,
            owner=user.name,
            permission_level=permission_level,
        )
        return {
            "status": "success",
            "document": {
                "id": doc.id,
                "title": doc.title,
                "filename": doc.filename,
                "status": doc.status.value,
                "chunk_count": doc.chunk_count,
            },
        }
    except Exception as e:
        logger.error(f"Upload and ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest-sample")
async def ingest_sample_data(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Ingest all sample HR documents for the pilot demo."""
    try:
        docs = await ingestion_service.ingest_sample_data(db)
        return {
            "status": "success",
            "documents_ingested": len(docs),
            "documents": [
                {
                    "id": d.id,
                    "title": d.title,
                    "status": d.status.value,
                    "chunk_count": d.chunk_count,
                }
                for d in docs
            ],
        }
    except Exception as e:
        logger.error(f"Sample data ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_documents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all documents."""
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [
        {
            "id": d.id,
            "title": d.title,
            "filename": d.filename,
            "file_type": d.file_type,
            "department": d.department,
            "owner": d.owner,
            "permission_level": d.permission_level.value,
            "status": d.status.value,
            "chunk_count": d.chunk_count,
            "version": d.version,
            "created_at": d.created_at.isoformat() if d.created_at else "",
            "updated_at": d.updated_at.isoformat() if d.updated_at else "",
        }
        for d in docs
    ]


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get document details."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": doc.id,
        "title": doc.title,
        "filename": doc.filename,
        "file_type": doc.file_type,
        "department": doc.department,
        "owner": doc.owner,
        "permission_level": doc.permission_level.value,
        "status": doc.status.value,
        "chunk_count": doc.chunk_count,
        "version": doc.version,
        "metadata": doc.metadata_json,
        "created_at": doc.created_at.isoformat() if doc.created_at else "",
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a document and its chunks from both SQLite and ChromaDB."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove from ChromaDB
    ingestion_service.delete_document_chunks(document_id)

    # Remove from SQLite
    db.delete(doc)
    db.commit()

    # Remove file
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except OSError:
            pass

    return {"status": "deleted", "document_id": document_id}


@router.get("/stats/collection")
async def collection_stats(
    user: User = Depends(get_current_user),
):
    """Get ChromaDB collection statistics."""
    stats = ingestion_service.get_collection_stats()
    return stats
