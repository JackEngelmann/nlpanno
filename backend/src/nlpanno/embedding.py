import logging
import time

from nlpanno import usecases

_LOGGER = logging.getLogger(__name__)


class EmbeddingProcessor:
	"""Process embeddings."""

	def __init__(
		self,
		embedding_function: usecases.EmbeddingFunction,
		sample_repository: usecases.SampleRepository,
	) -> None:
		self._embedding_function = embedding_function
		self._sample_repository = sample_repository

	def loop(self) -> None:
		"""Loop until all samples are embedded."""
		while True:
			did_work = self._process()
			if not did_work:
				self._sleep()

	def _process(self) -> bool:
		"""Start the embedding processor."""
		with self._sample_repository as sample_repository:
			use_case = usecases.EmbedAllSamplesUseCase(sample_repository, self._embedding_function)
			did_work = use_case()
		return did_work

	def _sleep(self) -> None:
		"""Sleep for 10 seconds."""
		_LOGGER.info("No work done, sleeping for 10 seconds.")
		time.sleep(10)
