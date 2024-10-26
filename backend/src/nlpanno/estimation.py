import time

from nlpanno import usecase, unitofwork


class EstimationProcessor:
    """Create estimations."""

    def __init__(
        self,
        unit_of_work_factory: unitofwork.UnitOfWorkFactory,
        embedding_aggregation_function: usecase.EmbeddingAggregationFunction,
        vector_similarity_function: usecase.VectorSimilarityFunction,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
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
        unit_of_work = self._unit_of_work_factory()
        usecase.estimate_samples(unit_of_work, self._embedding_aggregation_function, self._vector_similarity_function)
