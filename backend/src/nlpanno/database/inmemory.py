from types import TracebackType
from typing import Self

from nlpanno import domain, infrastructure, usecases


class InMemorySampleRepository(usecases.SampleRepository):
    """Sample repository using an in-memory list."""

    def __init__(self) -> None:
        self._samples: list[domain.Sample] = []

    def get_by_id(self, id_: domain.Id) -> domain.Sample:
        for sample in self._samples:
            if sample.id == id_:
                return sample
        raise ValueError(f"Sample with id {id_} not found")

    def update(self, sample: domain.Sample) -> None:
        for i, existing_sample in enumerate(self._samples):
            if existing_sample.id == sample.id:
                self._samples[i] = sample
                return
        raise ValueError(f"Sample with id {sample.id} not found")

    def create(self, sample: domain.Sample) -> None:
        self._samples.append(sample)

    def find(self, query: usecases.SampleQuery = usecases.SampleQuery()) -> tuple[domain.Sample, ...]:
        return tuple(sample for sample in self._samples if self._sample_matches_query(sample, query))
    
    def _sample_matches_query(self, sample: domain.Sample, query: usecases.SampleQuery) -> bool:
        if query.has_label is True and sample.text_class is None:
            return False
        elif query.has_label is False and sample.text_class is not None:
            return False
        if query.has_embedding is True and sample.embedding is None:
            return False
        elif query.has_embedding is False and sample.embedding is not None:
            return False
        return True


class InMemorySession(infrastructure.Session):
    def __init__(self) -> None:
        self._sample_repository = InMemorySampleRepository()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[Exception] | None,
        exc_value: Exception | None,
        traceback: TracebackType | None,
    ) -> None:
        pass

    @property
    def sample_repository(self) -> InMemorySampleRepository:
        return self._sample_repository

    def commit(self) -> None:
        pass

    def create_tables(self) -> None:
        pass


class InMemorySessionFactory(infrastructure.SessionFactory):
    def __init__(self) -> None:
        self._session = InMemorySession()

    def __call__(self) -> infrastructure.Session:
        return self._session
