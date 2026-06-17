"""
Citation extraction and formatting utilities.
"""

import re
from typing import List, Dict, Any


def format_citations(
    retrieved_chunks: List[Dict[str, Any]],
    answer_text: str
) -> List[Dict[str, Any]]:
    """
    Build citation objects from retrieved chunks.
    Each citation maps to a source document section.
    """
    citations = []
    seen = set()

    for i, chunk in enumerate(retrieved_chunks):
        doc_title = chunk.get("document_title", "Unknown Document")
        section = chunk.get("section_title", "")
        key = f"{doc_title}|{section}"

        if key in seen:
            continue
        seen.add(key)

        citations.append({
            "index": len(citations) + 1,
            "document_title": doc_title,
            "section_title": section,
            "parent_section": chunk.get("parent_section", ""),
            "excerpt": _truncate(chunk.get("content", ""), 300),
            "document_id": chunk.get("document_id", ""),
            "relevance_score": round(chunk.get("score", 0.0), 4),
            "permission_level": chunk.get("permission_level", "all_employees"),
        })

    return citations


def _truncate(text: str, max_length: int) -> str:
    """Truncate text to max_length, ending at a word boundary."""
    if len(text) <= max_length:
        return text
    truncated = text[:max_length]
    last_space = truncated.rfind(" ")
    if last_space > max_length * 0.6:
        truncated = truncated[:last_space]
    return truncated + "..."


def add_citation_markers(answer: str, citations: List[Dict[str, Any]]) -> str:
    """
    Add citation markers [1], [2], etc. to the answer text
    based on which sources are referenced.
    """
    # Simple approach: append citation numbers at the end of relevant sentences
    if not citations:
        return answer

    # Add a citation reference section at the end
    ref_lines = []
    for c in citations:
        ref_lines.append(
            f"[{c['index']}] {c['document_title']}"
            + (f" — {c['section_title']}" if c['section_title'] else "")
        )

    return answer
