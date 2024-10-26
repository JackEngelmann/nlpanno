import logging

from nlpanno.application import usecase, unitofwork
from nlpanno import worker

# TODO: use different logger.
_LOGGER = logging.getLogger("nlpanno")


class EstimationWorker(worker.Worker):
    """Worker for estimation."""

    def __init__(self, unit_of_work_factory: unitofwork.UnitOfWorkFactory) -> None:
        super().__init__(logger=_LOGGER, name="estimation", sleep_time=10)
        self._unit_of_work_factory = unit_of_work_factory

    def _process(self) -> worker.ProcessResult:
        """Process the worker."""
        unit_of_work = self._unit_of_work_factory()
        usecase.estimate_samples(unit_of_work)
        return worker.ProcessResult.FINISHED_WORK
