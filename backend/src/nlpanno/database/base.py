"""Base classes for databases."""

from nlpanno import domain
import abc


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
	
	@abc.abstractmethod
	def create(self, sample: domain.Sample) -> None:
		"""Create a sample."""
		raise NotImplementedError()

