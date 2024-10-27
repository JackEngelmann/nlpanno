import abc
from types import TracebackType
from typing import Self

from nlpanno.domain import repository


class UnitOfWork(abc.ABC):
    """Base class for a unit of work."""

    @abc.abstractmethod
    def __enter__(self) -> Self:
        raise NotImplementedError()

    @abc.abstractmethod
    def __exit__(
        self,
        exc_type: type[Exception] | None,
        exc_value: Exception | None,
        traceback: TracebackType | None,
    ) -> None:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def samples(self) -> repository.SampleRepository:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def annotation_tasks(self) -> repository.AnnotationTaskRepository:
        raise NotImplementedError()

    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def create_tables(self) -> None:
        raise NotImplementedError()
