import logging

from nlpanno import worker
from nlpanno.application import service, unitofwork, usecase

# TODO: use different logger.
_LOGGER = logging.getLogger("nlpanno")


class EmbeddingWorker(worker.Worker):
    """Worker for embedding."""

    def __init__(
        self,
        embedding_service: service.EmbeddingService,
        unit_of_work_factory: unitofwork.UnitOfWorkFactory,
    ) -> None:
        super().__init__(logger=_LOGGER, name="embedding", sleep_time=10)
        unit_of_work = unit_of_work_factory()
        self._embed_all_samples_use_case = usecase.EmbedAllSamplesUseCase(
            embedding_service, unit_of_work
        )

    def _process(self) -> worker.ProcessResult:
        """Process the worker."""
        # TODO: should the use case return the process result?
        did_work = self._embed_all_samples_use_case.execute(self._unit_of_work)
        if did_work:
            return worker.ProcessResult.FINISHED_WORK
        return worker.ProcessResult.NOTHING_TO_DO
