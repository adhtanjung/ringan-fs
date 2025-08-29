"""
Embedding Service for Text Vectorization
Handles text preprocessing and embedding generation using sentence-transformers
"""

import logging
from typing import List, Dict, Optional, Union
import numpy as np
from sentence_transformers import SentenceTransformer
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers"""

    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self.model_name = settings.EMBEDDING_MODEL
        self.vector_size = 384  # all-MiniLM-L6-v2 output size
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def initialize(self) -> bool:
        """Initialize the embedding model"""
        try:
            logger.info(f"🔄 Loading embedding model: {self.model_name}")

            # Load model in thread to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                self.executor,
                SentenceTransformer,
                self.model_name
            )

            logger.info("✅ Embedding model loaded successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {str(e)}")
            return False

    def preprocess_text(self, text: str) -> str:
        """Preprocess text for embedding generation"""
        if not text:
            return ""

        # Basic preprocessing for Indonesian text
        text = text.strip()
        text = text.lower()

        # Remove extra whitespace
        text = " ".join(text.split())

        return text

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text"""
        try:
            if not self.model:
                await self.initialize()

            if not text:
                return None

            # Preprocess text
            processed_text = self.preprocess_text(text)

            if not processed_text:
                return None

            # Generate embedding in thread
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                self.executor,
                self.model.encode,
                processed_text
            )

            # Convert to list of floats
            embedding_list = embedding.tolist()

            return embedding_list

        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {str(e)}")
            return None

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 16
    ) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts in batches"""
        try:
            if not self.model:
                await self.initialize()

            if not texts:
                return []

            # Preprocess all texts
            processed_texts = [self.preprocess_text(text) for text in texts]
            processed_texts = [text for text in processed_texts if text]

            if not processed_texts:
                return [None] * len(texts)

            # Generate embeddings in batches
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                self.executor,
                self.model.encode,
                processed_texts
            )

            # Convert to list of lists
            embedding_lists = embeddings.tolist()

            # Map back to original text positions
            result = []
            text_index = 0
            for original_text in texts:
                if original_text and self.preprocess_text(original_text):
                    result.append(embedding_lists[text_index])
                    text_index += 1
                else:
                    result.append(None)

            return result

        except Exception as e:
            logger.error(f"❌ Failed to generate batch embeddings: {str(e)}")
            return [None] * len(texts)

    async def generate_embedding_with_metadata(
        self,
        text: str,
        metadata: Dict
    ) -> Optional[Dict]:
        """Generate embedding with metadata"""
        try:
            embedding = await self.generate_embedding(text)

            if embedding is None:
                return None

            return {
                "text": text,
                "embedding": embedding,
                "metadata": metadata,
                "model": self.model_name,
                "vector_size": self.vector_size
            }

        except Exception as e:
            logger.error(f"❌ Failed to generate embedding with metadata: {str(e)}")
            return None

    async def generate_embeddings_with_metadata_batch(
        self,
        text_metadata_pairs: List[Dict]
    ) -> List[Optional[Dict]]:
        """Generate embeddings for multiple text-metadata pairs"""
        try:
            texts = [pair["text"] for pair in text_metadata_pairs]
            embeddings = await self.generate_embeddings_batch(texts)

            results = []
            for i, (pair, embedding) in enumerate(zip(text_metadata_pairs, embeddings)):
                if embedding is not None:
                    results.append({
                        "text": pair["text"],
                        "embedding": embedding,
                        "metadata": pair["metadata"],
                        "model": self.model_name,
                        "vector_size": self.vector_size
                    })
                else:
                    results.append(None)

            return results

        except Exception as e:
            logger.error(f"❌ Failed to generate batch embeddings with metadata: {str(e)}")
            return [None] * len(text_metadata_pairs)

    def calculate_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            if not embedding1 or not embedding2:
                return 0.0

            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(similarity)

        except Exception as e:
            logger.error(f"❌ Failed to calculate similarity: {str(e)}")
            return 0.0

    def get_model_info(self) -> Dict:
        """Get information about the embedding model"""
        return {
            "model_name": self.model_name,
            "vector_size": self.vector_size,
            "loaded": self.model is not None
        }

    async def close(self):
        """Clean up resources"""
        if self.executor:
            self.executor.shutdown(wait=True)
            logger.info("🔌 Closed embedding service")


# Global embedding service instance
embedding_service = EmbeddingService()
