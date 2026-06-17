"""
Hybrid retrieval service.
Combines dense vector search (ChromaDB) + sparse keyword search (BM25) + cross-encoder reranking.
"""

import logging
import time
from typing import List, Dict, Any, Optional

import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

from app.config import settings
from app.services.embeddings import embedding_service
from app.services.permissions import filter_chunks_by_permission, get_allowed_permission_levels
from app.models import UserRole

logger = logging.getLogger(__name__)


class RetrievalService:
    """Hybrid retrieval with dense + sparse search and cross-encoder reranking."""

    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self.collection = self.chroma_client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        # Load cross-encoder reranker (free, local model)
        self._reranker = None

    @property
    def reranker(self):
        """Lazy-load the cross-encoder reranker."""
        if self._reranker is None:
            logger.info("Loading cross-encoder reranker model...")
            self._reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            logger.info("Reranker loaded successfully")
        return self._reranker

    async def hybrid_search(
        self,
        query: str,
        user_role: UserRole = UserRole.EMPLOYEE,
        top_k: int = None,
        rerank_top_k: int = None,
        department_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Full hybrid retrieval pipeline:
        1. Dense vector search via ChromaDB
        2. BM25 keyword search
        3. Merge results
        4. Apply permission filters
        5. Cross-encoder reranking
        """
        top_k = top_k or settings.retrieval_top_k
        rerank_top_k = rerank_top_k or settings.rerank_top_k
        start_time = time.time()

        # Build ChromaDB where filter for permissions
        allowed_levels = get_allowed_permission_levels(user_role)
        where_filter = {"permission_level": {"$in": allowed_levels}}

        if department_filter:
            where_filter = {
                "$and": [
                    {"permission_level": {"$in": allowed_levels}},
                    {"department": department_filter},
                ]
            }

        # 1. Dense search via ChromaDB
        query_embedding = await embedding_service.embed_text(query)
        dense_results = self._dense_search(query_embedding, top_k, where_filter)
        dense_time = time.time() - start_time

        # 2. BM25 keyword search on the same collection
        bm25_start = time.time()
        keyword_results = self._keyword_search(query, top_k, allowed_levels, department_filter)
        bm25_time = time.time() - bm25_start

        # 3. Merge results (reciprocal rank fusion)
        merged = self._merge_results(dense_results, keyword_results)

        # 4. Permission filter (double-check)
        filtered = filter_chunks_by_permission(merged, user_role)

        # 5. Rerank with cross-encoder
        rerank_start = time.time()
        reranked = self._rerank(query, filtered, rerank_top_k)
        rerank_time = time.time() - rerank_start

        total_time = time.time() - start_time

        return {
            "results": reranked,
            "metadata": {
                "query": query,
                "total_candidates": len(merged),
                "after_permission_filter": len(filtered),
                "final_results": len(reranked),
                "dense_search_time_ms": round(dense_time * 1000),
                "bm25_search_time_ms": round(bm25_time * 1000),
                "rerank_time_ms": round(rerank_time * 1000),
                "total_time_ms": round(total_time * 1000),
            },
        }

    def _dense_search(
        self,
        query_embedding: List[float],
        top_k: int,
        where_filter: dict,
    ) -> List[Dict[str, Any]]:
        """Vector similarity search via ChromaDB."""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            logger.warning(f"Dense search with filter failed: {e}. Trying without filter.")
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )

        chunks = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if results["distances"] else 0
                # ChromaDB cosine distance: lower = more similar
                score = 1.0 - distance
                chunks.append({
                    "id": doc_id,
                    "content": results["documents"][0][i],
                    "score": score,
                    "source": "dense",
                    **(results["metadatas"][0][i] if results["metadatas"] else {}),
                })

        return chunks

    def _keyword_search(
        self,
        query: str,
        top_k: int,
        allowed_levels: List[str],
        department_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """BM25 keyword search over the ChromaDB collection."""
        try:
            # Get all documents from collection for BM25
            all_docs = self.collection.get(
                include=["documents", "metadatas"],
                limit=10000,  # Reasonable limit for BM25
            )

            if not all_docs or not all_docs["documents"]:
                return []

            # Filter by permissions first
            filtered_indices = []
            for i, meta in enumerate(all_docs["metadatas"]):
                perm = meta.get("permission_level", "all_employees")
                dept = meta.get("department", "")
                if perm in allowed_levels:
                    if department_filter is None or dept == department_filter:
                        filtered_indices.append(i)

            if not filtered_indices:
                return []

            filtered_docs = [all_docs["documents"][i] for i in filtered_indices]
            filtered_ids = [all_docs["ids"][i] for i in filtered_indices]
            filtered_metas = [all_docs["metadatas"][i] for i in filtered_indices]

            # Build BM25 index
            tokenized_docs = [doc.lower().split() for doc in filtered_docs]
            bm25 = BM25Okapi(tokenized_docs)

            # Score query
            tokenized_query = query.lower().split()
            scores = bm25.get_scores(tokenized_query)

            # Get top-k
            scored_indices = sorted(
                range(len(scores)), key=lambda i: scores[i], reverse=True
            )[:top_k]

            chunks = []
            for idx in scored_indices:
                if scores[idx] > 0:
                    chunks.append({
                        "id": filtered_ids[idx],
                        "content": filtered_docs[idx],
                        "score": float(scores[idx]),
                        "source": "bm25",
                        **filtered_metas[idx],
                    })

            return chunks

        except Exception as e:
            logger.warning(f"BM25 search failed: {e}")
            return []

    def _merge_results(
        self,
        dense_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Merge dense and keyword results using reciprocal rank fusion."""
        scored = {}
        k = 60  # RRF constant

        # Score dense results
        for rank, chunk in enumerate(dense_results):
            chunk_id = chunk["id"]
            rrf_score = 1.0 / (k + rank + 1)
            if chunk_id in scored:
                scored[chunk_id]["rrf_score"] += rrf_score
                scored[chunk_id]["sources"].append("dense")
            else:
                scored[chunk_id] = {**chunk, "rrf_score": rrf_score, "sources": ["dense"]}

        # Score keyword results
        for rank, chunk in enumerate(keyword_results):
            chunk_id = chunk["id"]
            rrf_score = 1.0 / (k + rank + 1)
            if chunk_id in scored:
                scored[chunk_id]["rrf_score"] += rrf_score
                scored[chunk_id]["sources"].append("bm25")
            else:
                scored[chunk_id] = {**chunk, "rrf_score": rrf_score, "sources": ["bm25"]}

        # Sort by RRF score
        merged = sorted(scored.values(), key=lambda x: x["rrf_score"], reverse=True)
        return merged

    def _rerank(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Rerank chunks using cross-encoder model."""
        if not chunks:
            return []

        if len(chunks) <= top_k:
            return chunks

        try:
            # Prepare pairs for cross-encoder
            pairs = [(query, chunk["content"]) for chunk in chunks]
            scores = self.reranker.predict(pairs)

            # Attach rerank scores
            for chunk, score in zip(chunks, scores):
                chunk["rerank_score"] = float(score)

            # Sort by rerank score and return top-k
            reranked = sorted(chunks, key=lambda x: x.get("rerank_score", 0), reverse=True)
            return reranked[:top_k]

        except Exception as e:
            logger.warning(f"Reranking failed, returning unranked results: {e}")
            return chunks[:top_k]


# Singleton instance
retrieval_service = RetrievalService()
