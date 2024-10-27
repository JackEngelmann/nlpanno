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
        self._unit_of_work_factory = unit_of_work_factory
        self._embedding_aggregation_service = embedding_aggregation_service
        self._vector_similarity_service = vector_similarity_service

    def _process(self) -> worker.ProcessResult:
        """Process the worker."""
        unit_of_work = self._unit_of_work_factory()
        usecase.estimate_samples(
            unit_of_work, self._embedding_aggregation_service, self._vector_similarity_service
        )
        return worker.ProcessResult.FINISHED_WORK
