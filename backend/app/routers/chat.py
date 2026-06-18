"""
Chat router — handles user queries, retrieval, and answer generation.
"""

import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, ChatSession, ChatMessage, AuditLog
from app.routers.auth import get_current_user
from app.services.retrieval import retrieval_service
from app.services.generation import generation_service
from app.services.actions import action_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


# ── Schemas ──

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    department_filter: Optional[str] = None
    stream: bool = False


class ChatResponse(BaseModel):
    answer: str
    citations: list
    confidence: str
    session_id: str
    message_id: str
    retrieval_metadata: dict
    generation_metadata: dict
    action_result: Optional[dict] = None


class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: str
    message_count: int


# ── Endpoints ──

@router.post("/query", response_model=ChatResponse)
async def chat_query(
    req: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Process a user query through the full RAG pipeline:
    1. Hybrid retrieval (dense + BM25 + rerank)
    2. Permission filtering
    3. Grounded answer generation with citations
    """
    start_time = time.time()

    # Get or create session
    if req.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == req.session_id,
            ChatSession.user_id == user.id,
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = ChatSession(user_id=user.id, title=req.query[:80])
        db.add(session)
        db.commit()
        db.refresh(session)

    # Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=req.query,
    )
    db.add(user_msg)
    db.commit()

    # 1. Hybrid retrieval
    retrieval_result = await retrieval_service.hybrid_search(
        query=req.query,
        user_role=user.role,
        department_filter=req.department_filter,
    )

    retrieved_chunks = retrieval_result["results"]
    retrieval_metadata = retrieval_result["metadata"]

    # 2. Classify intent
    intent = await action_service.classify_intent(req.query)

    # 3. Generate grounded answer or execute action
    action_result_dict = None
    if intent in ["DRAFT_EMAIL", "CREATE_TICKET"]:
        action_out = await action_service.execute_action(intent, req.query, retrieved_chunks)
        gen_result = {
            "answer": "I have drafted the requested item for you.",
            "citations": [],
            "confidence": "high",
            "metadata": {"model": "llama3.2", "generation_time_ms": 0}
        }
        action_result_dict = action_out
    else:
        gen_result = await generation_service.generate_answer(
            query=req.query,
            retrieved_chunks=retrieved_chunks,
        )

    total_time = time.time() - start_time

    # Save assistant message
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=gen_result["answer"],
        citations=gen_result["citations"],
        retrieval_metadata={
            **retrieval_metadata,
            "total_pipeline_time_ms": round(total_time * 1000),
            "action_result": action_result_dict
        },
    )
    db.add(assistant_msg)

    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action="query",
        target_type="chat",
        target_id=session.id,
        details={
            "query": req.query,
            "confidence": gen_result["confidence"],
            "citations_count": len(gen_result["citations"]),
            "retrieval_time_ms": retrieval_metadata.get("total_time_ms", 0),
            "generation_time_ms": gen_result["metadata"].get("generation_time_ms", 0),
        },
    )
    db.add(audit)
    db.commit()
    db.refresh(assistant_msg)

    return ChatResponse(
        answer=gen_result["answer"],
        citations=gen_result["citations"],
        confidence=gen_result["confidence"],
        session_id=session.id,
        message_id=assistant_msg.id,
        retrieval_metadata=retrieval_metadata,
        generation_metadata=gen_result["metadata"],
        action_result=action_result_dict,
    )


@router.post("/query/stream")
async def chat_query_stream(
    req: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Stream chat response token-by-token for real-time UI."""
    # Retrieve first (non-streaming)
    retrieval_result = await retrieval_service.hybrid_search(
        query=req.query,
        user_role=user.role,
        department_filter=req.department_filter,
    )

    retrieved_chunks = retrieval_result["results"]

    # 2. Classify intent
    intent = await action_service.classify_intent(req.query)

    # Stream the answer
    async def event_stream():
        # Send retrieval metadata first
        import json
        yield f"data: {json.dumps({'type': 'retrieval', 'metadata': retrieval_result['metadata']})}\n\n"

        if intent in ["DRAFT_EMAIL", "CREATE_TICKET"]:
            # For actions, we execute synchronously and return the result as a single token for simplicity
            action_out = await action_service.execute_action(intent, req.query, retrieved_chunks)
            yield f"data: {json.dumps({'type': 'action', 'content': action_out})}\n\n"
            yield f"data: {json.dumps({'type': 'token', 'content': 'I have drafted the requested item for you.'})}\n\n"
            yield f"data: {json.dumps({'type': 'citations', 'content': []})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        else:
            async for token_json in generation_service.generate_answer_stream(
                query=req.query,
                retrieved_chunks=retrieved_chunks,
            ):
                yield f"data: {token_json}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/sessions")
async def list_sessions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all chat sessions for the current user."""
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user.id)
        .order_by(ChatSession.updated_at.desc())
        .limit(50)
        .all()
    )

    result = []
    for s in sessions:
        msg_count = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).count()
        result.append({
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at.isoformat() if s.created_at else "",
            "updated_at": s.updated_at.isoformat() if s.updated_at else "",
            "message_count": msg_count,
        })

    return result


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get all messages in a chat session."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "citations": m.citations or [],
            "retrieval_metadata": m.retrieval_metadata or {},
            "created_at": m.created_at.isoformat() if m.created_at else "",
        }
        for m in messages
    ]


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a chat session and all its messages."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(session)
    db.commit()
    return {"status": "deleted"}
