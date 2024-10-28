from types import TracebackType
from typing import Self

from nlpanno.application import unitofwork
from nlpanno.domain import model, repository


class InMemorySampleRepository(repository.SampleRepository):
    """Sample repository using an in-memory list."""

    def __init__(self) -> None:
        self._samples: list[model.Sample] = []

    def get_by_id(self, id_: model.Id) -> model.Sample:
        for sample in self._samples:
            if sample.id == id_:
                return sample
        raise ValueError(f"Sample with id {id_} not found")

    def update(self, sample: model.Sample) -> None:
        for i, existing_sample in enumerate(self._samples):
            if existing_sample.id == sample.id:
                self._samples[i] = sample
                return
        raise ValueError(f"Sample with id {sample.id} not found")

    def create(self, sample: model.Sample) -> None:
        self._samples.append(sample)

    def find(self, query: repository.SampleQuery | None = None) -> tuple[model.Sample, ...]:
        if query is None:
            return tuple(self._samples)
        return tuple(
            sample for sample in self._samples if self._sample_matches_query(sample, query)
        )

    def _sample_matches_query(self, sample: model.Sample, query: repository.SampleQuery) -> bool:
        label_matches = self._sample_matches_has_label_filter(sample, query)
        embedding_matches = self._sample_matches_has_embedding_filter(sample, query)
        task_id_matches = self._sample_matches_task_id_filter(sample, query)
        return label_matches and embedding_matches and task_id_matches

    def _sample_matches_has_label_filter(
        self, sample: model.Sample, query: repository.SampleQuery
    ) -> bool:
        if query.has_label is None:
            return True
        sample_has_label = sample.text_class is not None
        return query.has_label == sample_has_label

    def _sample_matches_has_embedding_filter(
        self, sample: model.Sample, query: repository.SampleQuery
    ) -> bool:
        if query.has_embedding is None:
            return True
        sample_has_embedding = sample.embedding is not None
        return query.has_embedding == sample_has_embedding

    def _sample_matches_task_id_filter(
        self, sample: model.Sample, query: repository.SampleQuery
    ) -> bool:
        if query.task_id is None:
            return True
        return sample.annotation_task_id == query.task_id


class InMemoryAnnotationTaskRepository(repository.AnnotationTaskRepository):
    """Annotation task repository using an in-memory list."""

    def __init__(self) -> None:
        self._tasks: list[model.AnnotationTask] = []

    def get_by_id(self, id_: model.Id) -> model.AnnotationTask:
        for task in self._tasks:
            if task.id == id_:
                return task
        raise ValueError(f"Annotation task with id {id_} not found")

    def update(self, task: model.AnnotationTask) -> None:
        for i, existing_task in enumerate(self._tasks):
            if existing_task.id == task.id:
                self._tasks[i] = task
                return
        raise ValueError(f"Annotation task with id {task.id} not found")

    def create(self, task: model.AnnotationTask) -> None:
        self._tasks.append(task)

    def find(self) -> tuple[model.AnnotationTask, ...]:
        return tuple(self._tasks)


class InMemoryUnitOfWork(unitofwork.UnitOfWork):
    def __init__(self) -> None:
        self._sample_repository = InMemorySampleRepository()
        self._annotation_task_repository = InMemoryAnnotationTaskRepository()

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
    def samples(self) -> InMemorySampleRepository:
        return self._sample_repository

    @property
    def annotation_tasks(self) -> InMemoryAnnotationTaskRepository:
        return self._annotation_task_repository

    def commit(self) -> None:
        pass

    def create_tables(self) -> None:
        pass
