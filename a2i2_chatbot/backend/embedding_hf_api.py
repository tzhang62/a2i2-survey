"""
Hugging Face Embedding API Wrapper
Calls HF Space for fast GPU-based sentence embeddings
"""

import os
import requests
import numpy as np
from typing import List
import time

# Use the same IQL Space for embeddings (it has /embed endpoint)
HF_EMBEDDING_SPACE_URL = os.getenv(
    "HUGGINGFACE_MODEL_ID",
    "tzhang62-iql-fire-rescue-api.hf.space"
)

# Handle both model ID and Space URL formats
if not HF_EMBEDDING_SPACE_URL.startswith("http"):
    HF_EMBEDDING_SPACE_URL = f"https://{HF_EMBEDDING_SPACE_URL}"

class EmbeddingHuggingFace:
    """Wrapper for Hugging Face Embedding Space API"""
    
    def __init__(self, space_url: str = None):
        self.space_url = space_url or HF_EMBEDDING_SPACE_URL
        self.embed_endpoint = f"{self.space_url}/embed"
        print(f"[EMBED-HF] Initialized with Space: {self.space_url}")
    
    def encode(
        self,
        texts: List[str],
        normalize_embeddings: bool = True,
        convert_to_numpy: bool = True,
        show_progress_bar: bool = False,
        batch_size: int = 32
    ) -> np.ndarray:
        """
        Encode texts using HF Space (mimics sentence-transformers interface)
        
        Args:
            texts: List of strings to embed
            normalize_embeddings: Whether to normalize (default: True)
            convert_to_numpy: Whether to return numpy array (default: True)
            show_progress_bar: Ignored (for compatibility)
            batch_size: Ignored (HF Space handles batching)
        
        Returns:
            numpy array of shape (len(texts), 384)
        """
        try:
            start_time = time.time()
            
            # Call HF Space API
            response = requests.post(
                self.embed_endpoint,
                json={
                    "texts": texts,
                    "normalize": normalize_embeddings
                },
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            embeddings = data["embeddings"]
            
            elapsed = time.time() - start_time
            print(f"[EMBED-HF] Encoded {len(texts)} texts in {elapsed:.2f}s (GPU)")
            
            if convert_to_numpy:
                return np.array(embeddings, dtype=np.float32)
            return embeddings
            
        except requests.exceptions.Timeout:
            print(f"[EMBED-HF] Timeout calling HF Space (>30s)")
            raise RuntimeError("HF Embedding Space timeout")
        except requests.exceptions.RequestException as e:
            print(f"[EMBED-HF] Request error: {e}")
            raise RuntimeError(f"HF Embedding Space error: {e}")
        except Exception as e:
            print(f"[EMBED-HF] Unexpected error: {e}")
            raise


def get_embedding_hf() -> EmbeddingHuggingFace:
    """Get HF embedding instance"""
    return EmbeddingHuggingFace()


# Test if HF API is available
try:
    HF_EMBEDDING_API_AVAILABLE = True
    print("[EMBED-HF] Embedding API wrapper loaded successfully")
except Exception as e:
    HF_EMBEDDING_API_AVAILABLE = False
    print(f"[EMBED-HF] Failed to load: {e}")

