"""Module implementing data types and databases."""

from nlpanno import domain
import abc
import copy


class SampleRepository(abc.ABC):
	"""Base class for all sample repositories."""

	@abc.abstractmethod
	def get_by_id(self, id_: domain.Id) -> domain.Sample:
		"""Get a sample by the unique identifier."""
		raise NotImplementedError()

	@abc.abstractmethod
	def get_all(self) -> tuple[domain.Sample, ...]:
		"""Find all samples."""
		raise NotImplementedError()

	@abc.abstractmethod
	def update(self, sample: domain.Sample) -> None:
		"""Update a sample."""
		raise NotImplementedError()

	def get_unlabeled(self) -> tuple[domain.Sample, ...]:
		"""
		Get all unlabeled samples.

		This is a naive implementation that does not make use of DB features. It can be
		overwritten by DB implementations that have more efficient ways to retrieve unlabeled
		samples.
		"""
		return tuple(sample for sample in self.get_all() if sample.text_class is None)


class InMemorySampleRepository(SampleRepository):
	"""Database implementation keeping the data in-memory."""

	def __init__(self, samples: tuple[domain.Sample, ...]) -> None:
		self._sample_by_id: dict[str, domain.Sample] = {sample.id: sample for sample in samples}

	def get_by_id(self, id_: domain.Id) -> domain.Sample:
		"""Get a sample by the unique identifier."""
		sample = self._sample_by_id.get(id_)
		if sample is None:
			raise ValueError(f"No sample with id {id_}")
		return copy.deepcopy(sample)

	def get_all(self) -> tuple[domain.Sample, ...]:
		"""Find all samples."""
		return tuple(self._sample_by_id.values())
	
	def update(self, sample: domain.Sample) -> None:
		"""Update a sample."""
		self._sample_by_id[sample.id] = sample
