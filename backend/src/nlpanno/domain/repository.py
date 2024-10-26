import abc
from dataclasses import dataclass

from . import model


@dataclass
class SampleQuery:
    """Query for finding samples."""

    has_label: bool | None = None
    has_embedding: bool | None = None


class SampleRepository(abc.ABC):
    """Base class for all sample repositories."""

    @abc.abstractmethod
    def get_by_id(self, id_: model.Id) -> model.Sample:
        """Get a sample by the unique identifier."""
        raise NotImplementedError()

    @abc.abstractmethod
    def find(self, query: SampleQuery | None = None) -> tuple[model.Sample, ...]:
        """Find samples by the given query."""
        raise NotImplementedError()

    @abc.abstractmethod
    def update(self, sample: model.Sample) -> None:
        """Update a sample."""
        raise NotImplementedError()

    @abc.abstractmethod
    def create(self, sample: model.Sample) -> None:
        """Create a sample."""
        raise NotImplementedError()
