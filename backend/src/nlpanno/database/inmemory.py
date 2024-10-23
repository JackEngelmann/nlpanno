import copy
from nlpanno import database, domain


class InMemorySampleRepository(database.SampleRepository):
	"""Database implementation keeping the data in-memory."""

	def __init__(self) -> None:
		self._sample_by_id: dict[str, domain.Sample] = {}

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
	
	def create(self, sample: domain.Sample) -> None:
		"""Create a sample."""
		self._sample_by_id[sample.id] = sample