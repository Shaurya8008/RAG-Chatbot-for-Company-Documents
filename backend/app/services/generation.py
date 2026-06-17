"""
Answer generation service using Ollama (free, local LLM).
Generates grounded answers with citations and uncertainty handling.
"""

import httpx
import json
import logging
import time
from typing import List, Dict, Any, AsyncGenerator

from app.config import settings
from app.utils.citations import format_citations

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an internal HR Knowledge Assistant for Acme Corporation. Your role is to answer employee questions using ONLY the provided context from company documents.

RULES:
1. Answer ONLY based on the provided context. Do not use outside knowledge.
2. If the context does not contain enough information to answer the question, say: "I don't have enough information in the available documents to answer this question. Please contact HR at hr@acmecorp.example.com for assistance."
3. When you use information from the context, reference it naturally (e.g., "According to the Employee Handbook..." or "The Leave Policy states...").
4. Be concise, professional, and helpful.
5. If the question is about a specific number, date, or policy detail, quote it exactly from the context.
6. Do not make up policies, numbers, or procedures that are not in the context.
7. If you find conflicting information across documents, mention both and suggest the employee verify with HR.
"""


def _build_context_prompt(query: str, chunks: List[Dict[str, Any]]) -> str:
    """Build the prompt with retrieved context."""
    context_parts = []
    for i, chunk in enumerate(chunks):
        doc_title = chunk.get("document_title", "Unknown")
        section = chunk.get("section_title", "")
        content = chunk.get("content", "")
        header = f"[Source {i+1}: {doc_title}"
        if section:
            header += f" — {section}"
        header += "]"
        context_parts.append(f"{header}\n{content}")

    context_text = "\n\n---\n\n".join(context_parts)

    return f"""Context from company documents:

{context_text}

---

Employee Question: {query}

Please provide a helpful, accurate answer based ONLY on the context above. Reference the source documents when citing specific information."""


class GenerationService:
    """Generate grounded answers using Ollama."""

    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_llm_model

    async def generate_answer(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate a grounded answer from retrieved context.
        Returns the answer text, citations, and metadata.
        """
        start_time = time.time()

        if not retrieved_chunks:
            return {
                "answer": "I couldn't find any relevant documents to answer your question. This might be because the topic isn't covered in the current document library, or you may not have access to the relevant documents. Please contact HR at hr@acmecorp.example.com for assistance.",
                "citations": [],
                "confidence": "no_results",
                "metadata": {
                    "model": self.model,
                    "generation_time_ms": 0,
                    "context_chunks_used": 0,
                },
            }

        # Build prompt
        user_prompt = _build_context_prompt(query, retrieved_chunks)

        # Call Ollama
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "top_p": 0.9,
                            "num_predict": 1024,
                        },
                    },
                )
                response.raise_for_status()
                data = response.json()
                answer_text = data.get("message", {}).get("content", "")

        except httpx.HTTPError as e:
            logger.error(f"Ollama generation failed: {e}")
            answer_text = "I'm sorry, I encountered an error generating a response. Please try again or contact IT support."

        generation_time = time.time() - start_time

        # Build citations
        citations = format_citations(retrieved_chunks, answer_text)

        # Determine confidence level
        confidence = self._assess_confidence(retrieved_chunks, answer_text)

        return {
            "answer": answer_text,
            "citations": citations,
            "confidence": confidence,
            "metadata": {
                "model": self.model,
                "generation_time_ms": round(generation_time * 1000),
                "context_chunks_used": len(retrieved_chunks),
            },
        }

    async def generate_answer_stream(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> AsyncGenerator[str, None]:
        """Stream the answer token-by-token for real-time UI display."""
        if not retrieved_chunks:
            yield json.dumps({
                "type": "answer",
                "content": "I couldn't find any relevant documents to answer your question.",
            })
            return

        user_prompt = _build_context_prompt(query, retrieved_chunks)

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        "stream": True,
                        "options": {
                            "temperature": 0.1,
                            "top_p": 0.9,
                            "num_predict": 1024,
                        },
                    },
                ) as response:
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                data = json.loads(line)
                                content = data.get("message", {}).get("content", "")
                                if content:
                                    yield json.dumps({"type": "token", "content": content})
                                if data.get("done", False):
                                    # Send citations at the end
                                    citations = format_citations(retrieved_chunks, "")
                                    yield json.dumps({
                                        "type": "citations",
                                        "content": citations,
                                    })
                                    yield json.dumps({"type": "done"})
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            yield json.dumps({
                "type": "error",
                "content": "Generation failed. Please try again.",
            })

    def _assess_confidence(
        self,
        chunks: List[Dict[str, Any]],
        answer: str,
    ) -> str:
        """Assess answer confidence based on retrieval quality signals."""
        if not chunks:
            return "no_results"

        # Check average relevance scores
        scores = [c.get("rerank_score", c.get("score", 0)) for c in chunks]
        avg_score = sum(scores) / len(scores) if scores else 0

        # Check for uncertainty phrases in the answer
        uncertainty_phrases = [
            "i don't have enough information",
            "not covered in",
            "i couldn't find",
            "please contact hr",
            "i'm not sure",
            "unable to find",
        ]
        has_uncertainty = any(phrase in answer.lower() for phrase in uncertainty_phrases)

        if has_uncertainty:
            return "low"
        elif avg_score > 0.7:
            return "high"
        elif avg_score > 0.4:
            return "medium"
        else:
            return "low"

    async def health_check(self) -> bool:
        """Check if Ollama LLM is available."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m.get("name", "").split(":")[0] for m in models]
                    return self.model in model_names
            return False
        except Exception:
            return False


# Singleton instance
generation_service = GenerationService()
