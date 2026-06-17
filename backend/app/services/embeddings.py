"""
Embedding service using Ollama's nomic-embed-text model (free, local).
"""

import httpx
import logging
from typing import List

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate embeddings using Ollama's nomic-embed-text model."""

    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_embed_model

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text string."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                )
                response.raise_for_status()
                data = response.json()
                return data["embedding"]
            except httpx.HTTPError as e:
                logger.error(f"Embedding request failed: {e}")
                raise RuntimeError(f"Failed to generate embedding: {e}")

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        return embeddings

    async def health_check(self) -> bool:
        """Check if Ollama is running and the model is available."""
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
embedding_service = EmbeddingService()
