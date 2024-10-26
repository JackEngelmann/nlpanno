import logging
import enum
from abc import abstractmethod
import time


class ProcessResult(enum.Enum):
    """The result of the process."""

    NOTHING_TO_DO = enum.auto()
    FINISHED_WORK = enum.auto()
    ERROR = enum.auto()


class Worker:
    """A worker."""

    def __init__(self, logger: logging.Logger, name: str, sleep_time: float, stop_on_error: bool = True) -> None:
        """Initialize the worker."""    
        self._logger = logger
        self._name = name
        self._sleep_time = sleep_time
        self._stop_on_error = stop_on_error
        self._result_handlers = {
            ProcessResult.NOTHING_TO_DO: self._handle_nothing_to_do,
            ProcessResult.FINISHED_WORK: self._handle_finished_work,
            ProcessResult.ERROR: self._handle_error,
        }

    def start(self) -> None:
        """Start the worker."""
        self._logger.info(f"Starting the worker {self._name}")
        while True:
            result = self._wrapped_process()
            self._handle_result(result)
    
    def _handle_nothing_to_do(self) -> None:
        """Handle the nothing to do result."""
        self._logger.info(f"Worker {self._name} did no work, sleeping for {self._sleep_time} seconds.")
        time.sleep(self._sleep_time)

    def _handle_finished_work(self) -> None:
        """Handle the finished work result."""
        self._logger.info(f"Worker {self._name} finished work.")

    def _handle_error(self) -> None:
        self._logger.error(f"Worker {self._name} failed to process.")
        if self._stop_on_error:
            self._logger.error(f"Worker {self._name} stopping due to error.")
            raise Exception("Worker failed")

    def _wrapped_process(self) -> ProcessResult:
        """Wrap the process method to log the start and end of the process."""
        self._logger.info(f"Worker {self._name} starting process.")

        try:
            result = self._process()
        except Exception as e:
            self._logger.error(f"Worker {self._name} failed to process: {e}")
            return ProcessResult.ERROR

        self._logger.info(f"Worker {self._name} finished process.")
        return result

    @abstractmethod
    def _process(self) -> ProcessResult:
        """Process the worker."""
        raise NotImplementedError("Subclasses must implement this method.")