import time

from nlpanno import infrastructure, usecases


class EstimationProcessor:
	"""Create estimations."""

	def __init__(
		self,
		session_factory: infrastructure.SessionFactory,
		embedding_aggregation_function: usecases.EmbeddingAggregationFunction,
		vector_similarity_function: usecases.VectorSimilarityFunction,
	) -> None:
		self._session_factory = session_factory
		self._embedding_aggregation_function = embedding_aggregation_function
		self._vector_similarity_function = vector_similarity_function

	def loop(self) -> None:
		"""Loop until all samples are embedded."""
		while True:
			self.process()
			time.sleep(10)

	def process(self) -> None:
		"""Start the embedding processor."""
		# TODO: check is class embeddings are same as in last run.
		# If yes, skip estimation.
		with self._session_factory() as session:
			use_case = usecases.EstimateSamplesUseCase(
				session.sample_repository,
				self._embedding_aggregation_function,
				self._vector_similarity_function,
			)
			use_case()
			session.commit()