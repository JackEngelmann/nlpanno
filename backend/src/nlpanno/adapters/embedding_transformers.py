from collections.abc import Sequence

import sentence_transformers
import torch

from nlpanno.application import service
from nlpanno.domain import model


class TransformersEmbeddingService(service.EmbeddingService):
    def __init__(self, model_name: str) -> None:
        self._transformer = sentence_transformers.SentenceTransformer(model_name)

    def embed_samples(self, samples: Sequence[model.Sample]) -> Sequence[model.Embedding]:
        texts = list(sample.text for sample in samples)
        return self._transformer.encode(texts, convert_to_tensor=True)  # type: ignore


class TransformersEmbeddingAggregationService(service.EmbeddingAggregationService):
    def aggregate_embeddings(self, embeddings: Sequence[model.Embedding]) -> model.Embedding:
        stacked = torch.stack(list(embeddings), dim=0)
        return torch.mean(stacked, dim=0)


class TransformersVectorSimilarityService(service.VectorSimilarityService):
    def calculate_similarity(
        self, sample_embedding: model.Embedding, class_embedding: model.Embedding
    ) -> float:
        return sentence_transformers.util.pytorch_cos_sim(class_embedding, sample_embedding).item()
