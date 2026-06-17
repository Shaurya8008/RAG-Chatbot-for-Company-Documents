"""
Section-aware chunking utilities.
Splits documents by headings and sections rather than naive fixed-size windows.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def chunk_markdown(
    text: str,
    filename: str = "",
    max_chunk_size: int = 512,
    overlap: int = 50,
) -> List[Dict[str, Any]]:
    """
    Section-aware chunking for markdown documents.
    Splits by headings to preserve context hierarchy.
    Falls back to size-based splitting for long sections.
    """
    chunks = []
    lines = text.split("\n")

    current_section = ""
    parent_section = ""
    current_content = []
    chunk_index = 0

    for line in lines:
        # Detect heading levels
        h1_match = re.match(r"^#\s+(.+)", line)
        h2_match = re.match(r"^##\s+(.+)", line)
        h3_match = re.match(r"^###\s+(.+)", line)

        if h1_match or h2_match:
            # Save previous section if it has content
            if current_content:
                section_text = "\n".join(current_content).strip()
                if section_text:
                    sub_chunks = _split_long_section(
                        section_text, current_section, parent_section,
                        filename, chunk_index, max_chunk_size, overlap
                    )
                    chunks.extend(sub_chunks)
                    chunk_index += len(sub_chunks)
                current_content = []

            if h1_match:
                parent_section = h1_match.group(1).strip()
                current_section = parent_section
            elif h2_match:
                current_section = h2_match.group(1).strip()

            current_content.append(line)

        elif h3_match:
            # Save previous sub-section
            if current_content:
                section_text = "\n".join(current_content).strip()
                if section_text:
                    sub_chunks = _split_long_section(
                        section_text, current_section, parent_section,
                        filename, chunk_index, max_chunk_size, overlap
                    )
                    chunks.extend(sub_chunks)
                    chunk_index += len(sub_chunks)
                current_content = []

            current_section = h3_match.group(1).strip()
            current_content.append(line)
        else:
            current_content.append(line)

    # Don't forget the last section
    if current_content:
        section_text = "\n".join(current_content).strip()
        if section_text:
            sub_chunks = _split_long_section(
                section_text, current_section, parent_section,
                filename, chunk_index, max_chunk_size, overlap
            )
            chunks.extend(sub_chunks)

    logger.info(f"Chunked '{filename}' into {len(chunks)} chunks")
    return chunks


def _split_long_section(
    text: str,
    section_title: str,
    parent_section: str,
    filename: str,
    start_index: int,
    max_chunk_size: int,
    overlap: int,
) -> List[Dict[str, Any]]:
    """Split a section that exceeds max_chunk_size into overlapping sub-chunks."""
    words = text.split()

    if len(words) <= max_chunk_size:
        return [{
            "content": text,
            "section_title": section_title,
            "parent_section": parent_section,
            "filename": filename,
            "chunk_index": start_index,
        }]

    chunks = []
    idx = start_index
    start = 0

    while start < len(words):
        end = min(start + max_chunk_size, len(words))
        chunk_text = " ".join(words[start:end])
        chunks.append({
            "content": chunk_text,
            "section_title": section_title,
            "parent_section": parent_section,
            "filename": filename,
            "chunk_index": idx,
        })
        idx += 1
        start += max_chunk_size - overlap

    return chunks


def chunk_plain_text(
    text: str,
    filename: str = "",
    max_chunk_size: int = 512,
    overlap: int = 50,
) -> List[Dict[str, Any]]:
    """
    Fallback chunking for plain text without heading structure.
    Uses paragraph-based splitting with size limits.
    """
    paragraphs = re.split(r"\n\s*\n", text)
    chunks = []
    current_chunk = []
    current_word_count = 0
    chunk_index = 0

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        words = paragraph.split()
        para_word_count = len(words)

        if current_word_count + para_word_count > max_chunk_size and current_chunk:
            # Save current chunk
            chunks.append({
                "content": "\n\n".join(current_chunk),
                "section_title": "",
                "parent_section": "",
                "filename": filename,
                "chunk_index": chunk_index,
            })
            chunk_index += 1

            # Keep overlap
            if overlap > 0 and current_chunk:
                last_chunk_words = current_chunk[-1].split()
                overlap_text = " ".join(last_chunk_words[-overlap:])
                current_chunk = [overlap_text]
                current_word_count = min(overlap, len(last_chunk_words))
            else:
                current_chunk = []
                current_word_count = 0

        current_chunk.append(paragraph)
        current_word_count += para_word_count

    if current_chunk:
        chunks.append({
            "content": "\n\n".join(current_chunk),
            "section_title": "",
            "parent_section": "",
            "filename": filename,
            "chunk_index": chunk_index,
        })

    logger.info(f"Chunked '{filename}' into {len(chunks)} chunks (plain text)")
    return chunks
