import logging

import nlpanno.container
from nlpanno import config, worker
from nlpanno.application import usecase

# TODO: use different logger.
_LOGGER = logging.getLogger("nlpanno")


class EstimationWorker(worker.Worker):
    """Worker for estimation."""

    def __init__(self, estimate_samples_use_case: usecase.EstimateSamplesUseCase) -> None:
        super().__init__(logger=_LOGGER, name="estimation", sleep_time=10)
        self._estimate_samples_use_case = estimate_samples_use_case

    def _process(self) -> worker.ProcessResult:
        """Process the worker."""
        self._estimate_samples_use_case.execute()
        return worker.ProcessResult.FINISHED_WORK


def run() -> None:
    """Run the estimation worker."""
    settings = config.ApplicationSettings()
    container = nlpanno.container.create_container(settings)
    estimate_samples_use_case = container.estimate_samples_use_case()
    estimation_worker = EstimationWorker(estimate_samples_use_case)
    estimation_worker.start()


if __name__ == "__main__":
    run()
