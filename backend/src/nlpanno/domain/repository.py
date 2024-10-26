import abc
from dataclasses import dataclass

from . import domain


@dataclass
class SampleQuery:
    """Query for finding samples."""

    has_label: bool | None = None
    has_embedding: bool | None = None


class SampleRepository(abc.ABC):
    """Base class for all sample repositories."""

    @abc.abstractmethod
    def get_by_id(self, id_: domain.Id) -> domain.Sample:
        """Get a sample by the unique identifier."""
        raise NotImplementedError()

    @abc.abstractmethod
    def find(self, query: SampleQuery | None = None) -> tuple[domain.Sample, ...]:
        """Find samples by the given query."""
        raise NotImplementedError()

    @abc.abstractmethod
    def update(self, sample: domain.Sample) -> None:
        """Update a sample."""
        raise NotImplementedError()

    @abc.abstractmethod
    def create(self, sample: domain.Sample) -> None:
        """Create a sample."""
        raise NotImplementedError()
