import logging

from nlpanno import worker
from nlpanno.application import unitofwork, usecase

# TODO: use different logger.
_LOGGER = logging.getLogger("nlpanno")


class EstimationWorker(worker.Worker):
    """Worker for estimation."""

    def __init__(
        self,
        unit_of_work_factory: unitofwork.UnitOfWorkFactory,
        embedding_aggregation_function: usecase.EmbeddingAggregationFunction,
        vector_similarity_function: usecase.VectorSimilarityFunction,
    ) -> None:
        super().__init__(logger=_LOGGER, name="estimation", sleep_time=10)
        self._unit_of_work_factory = unit_of_work_factory
        self._embedding_aggregation_function = embedding_aggregation_function
        self._vector_similarity_function = vector_similarity_function

    def _process(self) -> worker.ProcessResult:
        """Process the worker."""
        unit_of_work = self._unit_of_work_factory()
        usecase.estimate_samples(
            unit_of_work, self._embedding_aggregation_function, self._vector_similarity_function
        )
        return worker.ProcessResult.FINISHED_WORK
