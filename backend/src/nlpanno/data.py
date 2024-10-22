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
	def get_all_samples(self) -> tuple[Sample, ...]:
		"""Find all samples."""
		raise NotImplementedError()

	@abc.abstractmethod
	def update_sample(self, sample: Sample) -> None:
		"""Update a sample."""
		raise NotImplementedError()

	def get_unlabeled_samples(self) -> tuple[Sample, ...]:
		"""
		Get all unlabeled samples.

		This is a naive implementation that does not make use of DB features. It can be
		overwritten by DB implementations that have more efficient ways to retrieve unlabeled
		samples.
		"""
		return tuple(sample for sample in self.get_all_samples() if sample.text_class is None)


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

	def get_all_samples(self) -> tuple[Sample, ...]:
		"""Find all samples."""
		return tuple(self._sample_by_id.values())
	
	def update_sample(self, sample: Sample) -> None:
		"""Update a sample."""
		self._sample_by_id[sample.id] = sample
