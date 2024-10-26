import logging
from collections.abc import Sequence

import sentence_transformers
import sqlalchemy
import torch

from nlpanno import (
    adapters,
    config,
    domain,
    sampling,
)
from nlpanno.application import unitofwork, usecase

_LOG = logging.getLogger("nlpanno")


# TODO: proper dependency injection.
class DependencyContainer:
    """Container for dependencies."""

    def __init__(self, settings: config.ApplicationSettings) -> None:
        self.settings = settings
        _LOG.info("Database URL: %s", self.settings.database_url)
        self._engine = sqlalchemy.create_engine(self.settings.database_url)

    def create_unit_of_work_factory(self) -> unitofwork.UnitOfWorkFactory:
        return adapters.SQLAlchemyUnitOfWorkFactory(self._engine)

    def create_embedding_function(self) -> usecase.EmbeddingFunction:
        model = sentence_transformers.SentenceTransformer(self.settings.embedding_model_name)
        _LOG.info("finished loading embedding model")

        def embedding_function(samples: Sequence[domain.Sample]) -> Sequence[domain.Embedding]:
            texts = list(sample.text for sample in samples)
            return model.encode(texts, convert_to_tensor=True)  # type: ignore

        return embedding_function

    def create_embedding_aggregation_function(self) -> usecase.EmbeddingAggregationFunction:
        def embedding_aggregation_function(
            embeddings: Sequence[domain.Embedding],
        ) -> domain.Embedding:
            stacked = torch.stack(list(embeddings), dim=0)
            return torch.mean(stacked, dim=0)

        return embedding_aggregation_function

    def create_vector_similarity_function(self) -> usecase.VectorSimilarityFunction:
        def vector_similarity_function(
            sample_embedding: domain.Embedding, class_embedding: domain.Embedding
        ) -> float:
            return sentence_transformers.util.pytorch_cos_sim(
                class_embedding, sample_embedding
            ).item()

        return vector_similarity_function

    def create_embedding_worker(self) -> adapters.EmbeddingWorker:
        embedding_function = self.create_embedding_function()
        unit_of_work_factory = self.create_unit_of_work_factory()
        return adapters.EmbeddingWorker(embedding_function, unit_of_work_factory)

    def create_estimation_worker(self) -> adapters.EstimationWorker:
        unit_of_work_factory = self.create_unit_of_work_factory()
        embedding_aggregation_function = self.create_embedding_aggregation_function()
        vector_similarity_function = self.create_vector_similarity_function()
        return adapters.EstimationWorker(
            unit_of_work_factory, embedding_aggregation_function, vector_similarity_function
        )

    def create_sampler(self) -> sampling.Sampler:
        return sampling.RandomSampler()
