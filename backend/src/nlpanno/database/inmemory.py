from types import TracebackType

from nlpanno import domain, usecases


class InMemorySampleRepository(usecases.SampleRepository):
	"""Sample repository using an in-memory list."""

	def __init__(self) -> None:
		self._samples: list[domain.Sample] = []

	def get_by_id(self, id_: domain.Id) -> domain.Sample:
		for sample in self._samples:
			if sample.id == id_:
				return sample
		raise ValueError(f"Sample with id {id_} not found")

	def get_all(self) -> tuple[domain.Sample, ...]:
		return tuple(self._samples)

	def update(self, sample: domain.Sample) -> None:
		for i, existing_sample in enumerate(self._samples):
			if existing_sample.id == sample.id:
				self._samples[i] = sample
				return
		raise ValueError(f"Sample with id {sample.id} not found")

	def get_unlabeled(self) -> tuple[domain.Sample, ...]:
		return tuple(sample for sample in self._samples if sample.text_class is None)

	def get_labeled(self) -> tuple[domain.Sample, ...]:
		return tuple(sample for sample in self._samples if sample.text_class is not None)

	def get_unembedded(self) -> tuple[domain.Sample, ...]:
		return tuple(sample for sample in self._samples if sample.embedding is None)

	def create(self, sample: domain.Sample) -> None:
		self._samples.append(sample)
