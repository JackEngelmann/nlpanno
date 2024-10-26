import logging

from nlpanno import worker
from nlpanno.application import unitofwork, usecase

# TODO: use different logger.
_LOGGER = logging.getLogger("nlpanno")


class EmbeddingWorker(worker.Worker):
    """Worker for embedding."""

    def __init__(
        self,
        embedding_function: usecase.EmbeddingFunction,
        unit_of_work_factory: unitofwork.UnitOfWorkFactory,
    ) -> None:
        super().__init__(logger=_LOGGER, name="embedding", sleep_time=10)
        self._embedding_function = embedding_function
        self._unit_of_work_factory = unit_of_work_factory

    def _process(self) -> worker.ProcessResult:
        """Process the worker."""
        unit_of_work = self._unit_of_work_factory()
        # TODO: should the use case return the process result?
        did_work = usecase.embed_all_samples(unit_of_work, self._embedding_function)
        if did_work:
            return worker.ProcessResult.FINISHED_WORK
        return worker.ProcessResult.NOTHING_TO_DO
