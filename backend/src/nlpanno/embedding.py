import logging
import time

from nlpanno import infrastructure, usecases

_LOGGER = logging.getLogger("nlpanno.embedding")


class EmbeddingProcessor:
	"""Process embeddings."""

	def __init__(
		self,
		embedding_function: usecases.EmbeddingFunction,
		session_factory: infrastructure.SessionFactory,
	) -> None:
		self._embedding_function = embedding_function
		self._session_factory = session_factory

	def loop(self) -> None:
		"""Loop until all samples are embedded."""
		_LOGGER.info("starting loop")
		while True:
			did_work = self._process()
			if not did_work:
				self._sleep()

	def _process(self) -> bool:
		"""Start the embedding processor."""
		_LOGGER.info("starting processing")
		with self._session_factory() as session:
			use_case = usecases.EmbedAllSamplesUseCase(session.sample_repository, self._embedding_function)
			did_work = use_case()
			session.commit()
		return did_work

	def _sleep(self) -> None:
		"""Sleep for 10 seconds."""
		_LOGGER.info("No work done, sleeping for 10 seconds.")
		time.sleep(10)
