from nlpanno import usecases
import time


class EstimationProcessor:
	"""Create estimations."""

	def __init__(
		self,
		sample_repository: usecases.SampleRepository,
		embedding_aggregation_function: usecases.EmbeddingAggregationFunction,
		vector_similarity_function: usecases.VectorSimilarityFunction,
	) -> None:
		self._sample_repository = sample_repository
		self._embedding_aggregation_function = embedding_aggregation_function
		self._vector_similarity_function = vector_similarity_function

	def loop(self) -> None:
		"""Loop until all samples are embedded."""
		while True:
			self.process()
			time.sleep(5)

	def process(self) -> None:
		"""Start the embedding processor."""
		# TODO: check is class embeddings are same as in last run.
		# If yes, skip estimation.
		with self._sample_repository as sample_repository:
			use_case = usecases.EstimateSamplesUseCase(
				sample_repository,
				self._embedding_aggregation_function,
				self._vector_similarity_function,
			)
			use_case()
