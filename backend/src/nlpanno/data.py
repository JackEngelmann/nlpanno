"""Module implementing data types and databases."""

# pylint: disable = invalid-name

import abc
import dataclasses
import uuid
from typing import Dict, Optional, Tuple, TypedDict

Id = str


def create_id() -> Id:
    """Create unique identifier."""
    return str(uuid.uuid4())


@dataclasses.dataclass
class Sample:
    """Data structure for a sample."""

    id: Id
    text: str
    text_class: Optional[str] = None
    text_class_predictions: Optional[Tuple[float, ...]] = None


class SampleFindCriteria(TypedDict, total=False):
    """Find criteria for a sample."""

    text_class: Optional[str]


@dataclasses.dataclass
class TaskConfig:
    """Data structure for a task configuration."""

    text_classes: Tuple[str, ...]


class Database(abc.ABC):
    """Base class for all databases."""

    @abc.abstractmethod
    def get_task_config(self) -> TaskConfig:
        """Get the task config."""
        raise NotImplementedError()

    @abc.abstractmethod
    def set_task_config(self, task_config: TaskConfig):
        """Set the task config."""
        raise NotImplementedError()

    @abc.abstractmethod
    def add_sample(self, sample: Sample) -> None:
        """Add a sample."""
        raise NotImplementedError()

    @abc.abstractmethod
    def get_sample_by_id(self, id_: Id) -> Sample:
        """Get a sample by the unique identifier."""
        raise NotImplementedError()

    @abc.abstractmethod
    def find_samples(
        self, criteria: Optional[SampleFindCriteria] = None
    ) -> Tuple[Sample, ...]:
        """Find samples given the criteria."""
        raise NotImplementedError()

    @abc.abstractmethod
    def update_sample(self, sample: Sample) -> None:
        """Update a sample."""
        raise NotImplementedError()


class InMemoryDatabase(Database):
    """Database implementation keeping the data in-memory."""

    def __init__(self) -> None:
        self._sample_by_id: Dict[str, Sample] = {}
        self._task_config: Optional[TaskConfig] = None

    def get_task_config(self) -> TaskConfig:
        """Get the task config."""
        if self._task_config is None:
            raise RuntimeError("Task config was not set.")
        return self._task_config

    def set_task_config(self, task_config: TaskConfig):
        """Set the task config."""
        self._task_config = task_config

    def add_sample(self, sample: Sample) -> None:
        """Add a sample."""
        self._sample_by_id[sample.id] = sample

    def get_sample_by_id(self, id_: Id) -> Sample:
        """Get a sample by the unique identifier."""
        sample = self._sample_by_id.get(id_)
        if sample is None:
            raise ValueError(f"No sample with id {id_}")
        return sample

    def find_samples(
        self, criteria: Optional[SampleFindCriteria] = None
    ) -> Tuple[Sample, ...]:
        """Find samples given the criteria."""
        if criteria is None:
            return tuple(self._sample_by_id.values())
        matches = []
        for sample in self._sample_by_id.values():
            text_class_matches = (
                "text_class" not in criteria
                or sample.text_class == criteria["text_class"]
            )
            if text_class_matches:
                matches.append(sample)
        return tuple(matches)

    def update_sample(self, sample: Sample) -> None:
        """Update a sample."""
        self._sample_by_id[sample.id] = sample
