import logging
from collections.abc import Sequence

import sentence_transformers
import sqlalchemy
import torch

from nlpanno import (
	config,
	database,
	domain,
	embedding,
	estimation,
	infrastructure,
	sampling,
	usecases,
)

_LOG = logging.getLogger("nlpanno")


# TODO: proper dependency injection.
class DependencyContainer:
	"""Container for dependencies."""

	def __init__(self, settings: config.ApplicationSettings) -> None:
		self.settings = settings
		_LOG.info("Database URL: %s", self.settings.database_url)
		self._engine = sqlalchemy.create_engine(self.settings.database_url)

	def create_session_factory(self) -> infrastructure.SessionFactory:
		return database.SQLAlchemySessionFactory(self._engine)

	def create_embedding_function(self) -> usecases.EmbeddingFunction:
		model = sentence_transformers.SentenceTransformer(self.settings.embedding_model_name)
		_LOG.info("finished loading embedding model")

		def embedding_function(samples: Sequence[domain.Sample]) -> Sequence[domain.Embedding]:
			texts = list(sample.text for sample in samples)
			return model.encode(texts, convert_to_tensor=True)  # type: ignore

		return embedding_function

	def create_embedding_aggregation_function(self) -> usecases.EmbeddingAggregationFunction:
		def embedding_aggregation_function(
			embeddings: Sequence[domain.Embedding],
		) -> domain.Embedding:
			stacked = torch.stack(list(embeddings), dim=0)
			return torch.mean(stacked, dim=0)

		return embedding_aggregation_function

	def create_vector_similarity_function(self) -> usecases.VectorSimilarityFunction:
		def vector_similarity_function(
			sample_embedding: domain.Embedding, class_embedding: domain.Embedding
		) -> float:
			return sentence_transformers.util.pytorch_cos_sim(
				class_embedding, sample_embedding
			).item()

		return vector_similarity_function

	def create_embedding_processor(self) -> embedding.EmbeddingProcessor:
		embedding_function = self.create_embedding_function()
		session_factory = self.create_session_factory()
		return embedding.EmbeddingProcessor(embedding_function, session_factory)

	def create_estimation_processor(self) -> estimation.EstimationProcessor:
		session_factory = self.create_session_factory()
		embedding_aggregation_function = self.create_embedding_aggregation_function()
		vector_similarity_function = self.create_vector_similarity_function()
		return estimation.EstimationProcessor(
			session_factory, embedding_aggregation_function, vector_similarity_function
		)

	def create_sampler(self) -> sampling.Sampler:
		return sampling.RandomSampler()
