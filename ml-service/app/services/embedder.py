import os
from abc import ABC, abstractmethod
from typing import List

import numpy as np


class EmbeddingStrategy(ABC):
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        raise NotImplementedError


class OpenAIEmbeddingStrategy(EmbeddingStrategy):
    async def embed(self, text: str) -> List[float]:
        # TODO: call OpenAI or Azure OpenAI embeddings API
        seed = hash(text) % 1000
        rng = np.random.default_rng(seed)
        return rng.normal(size=16).astype(float).tolist()


class LocalEmbeddingStrategy(EmbeddingStrategy):
    async def embed(self, text: str) -> List[float]:
        # TODO: integrate sentence-transformers model
        seed = (hash(text) + 42) % 1000
        rng = np.random.default_rng(seed)
        return rng.normal(size=16).astype(float).tolist()
