import logging
import time

from nlpanno.application import usecase, unitofwork

_LOGGER = logging.getLogger("nlpanno.embedding")


class EmbeddingProcessor:
    """Process embeddings."""

    def __init__(
        self,
        embedding_function: usecase.EmbeddingFunction,
        unit_of_work_factory: unitofwork.UnitOfWorkFactory,
    ) -> None:
        self._embedding_function = embedding_function
        self._unit_of_work_factory = unit_of_work_factory

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
        unit_of_work = self._unit_of_work_factory()
        return usecase.embed_all_samples(unit_of_work, self._embedding_function)

    def _sleep(self) -> None:
        """Sleep for 10 seconds."""
        _LOGGER.info("No work done, sleeping for 10 seconds.")
        time.sleep(10)
