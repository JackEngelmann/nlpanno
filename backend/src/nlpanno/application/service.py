from abc import ABC, abstractmethod
from collections.abc import Sequence

from nlpanno.domain import model


class EmbeddingService(ABC):
    @abstractmethod
    def embed_samples(self, samples: Sequence[model.Sample]) -> Sequence[model.Embedding]:
        raise NotImplementedError()


class EmbeddingAggregationService(ABC):
    @abstractmethod
    def aggregate_embeddings(self, embeddings: Sequence[model.Embedding]) -> model.Embedding:
        raise NotImplementedError()


class VectorSimilarityService(ABC):
    @abstractmethod
    def calculate_similarity(
        self, sample_embedding: model.Embedding, class_embedding: model.Embedding
    ) -> float:
        raise NotImplementedError()


class SamplingService(ABC):
    @abstractmethod
    def sample(self, samples: Sequence[model.Sample]) -> model.Id | None:
        raise NotImplementedError()
