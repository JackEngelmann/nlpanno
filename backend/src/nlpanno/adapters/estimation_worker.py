import logging

from nlpanno import worker
from nlpanno.application import service, unitofwork, usecase

# TODO: use different logger.
_LOGGER = logging.getLogger("nlpanno")


class EstimationWorker(worker.Worker):
    """Worker for estimation."""

    def __init__(
        self,
        unit_of_work_factory: unitofwork.UnitOfWorkFactory,
        embedding_aggregation_service: service.EmbeddingAggregationService,
        vector_similarity_service: service.VectorSimilarityService,
    ) -> None:
        super().__init__(logger=_LOGGER, name="estimation", sleep_time=10)
        unit_of_work = unit_of_work_factory()
        self._estimate_samples_use_case = usecase.EstimateSamplesUseCase(
            embedding_aggregation_service, vector_similarity_service, unit_of_work
        )

    def _process(self) -> worker.ProcessResult:
        """Process the worker."""
        did_work = self._estimate_samples_use_case.execute(self._unit_of_work)
        if did_work:
            return worker.ProcessResult.FINISHED_WORK
        return worker.ProcessResult.NOTHING_TO_DO
