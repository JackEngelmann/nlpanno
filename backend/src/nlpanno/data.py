"""Module implementing data types and databases."""

import abc
import copy
import dataclasses
import uuid
from typing import Optional, TypedDict

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
	text_class_predictions: Optional[tuple[float, ...]] = None


class SampleFindCriteria(TypedDict, total=False):
	"""Find criteria for a sample."""

	text_class: Optional[str]


@dataclasses.dataclass
class TaskConfig:
	"""Data structure for a task configuration."""

	text_classes: tuple[str, ...]


class Database(abc.ABC):
	"""Base class for all databases."""

	@abc.abstractmethod
	def get_sample_by_id(self, id_: Id) -> Sample:
		"""Get a sample by the unique identifier."""
		raise NotImplementedError()

	@abc.abstractmethod
	def find_samples(self, criteria: Optional[SampleFindCriteria] = None) -> tuple[Sample, ...]:
		"""Find samples given the criteria."""
		raise NotImplementedError()

	@abc.abstractmethod
	def update_sample(self, sample: Sample) -> None:
		"""Update a sample."""
		raise NotImplementedError()


class InMemoryDatabase(Database):
	"""Database implementation keeping the data in-memory."""

	def __init__(self, samples: tuple[Sample, ...]) -> None:
		self._sample_by_id: dict[str, Sample] = {sample.id: sample for sample in samples}

	def get_sample_by_id(self, id_: Id) -> Sample:
		"""Get a sample by the unique identifier."""
		sample = self._sample_by_id.get(id_)
		if sample is None:
			raise ValueError(f"No sample with id {id_}")
		return copy.deepcopy(sample)

	def find_samples(self, criteria: Optional[SampleFindCriteria] = None) -> tuple[Sample, ...]:
		"""Find samples given the criteria."""
		if criteria is None:
			return tuple(self._sample_by_id.values())
		matches = []
		for sample in self._sample_by_id.values():
			text_class_matches = (
				"text_class" not in criteria or sample.text_class == criteria["text_class"]
			)
			if text_class_matches:
				matches.append(copy.deepcopy(sample))
		return tuple(matches)

	def update_sample(self, sample: Sample) -> None:
		"""Update a sample."""
		self._sample_by_id[sample.id] = sample
