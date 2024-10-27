import collections
import logging

from nlpanno.application import service, unitofwork
from nlpanno.domain import model, repository

_LOGGER = logging.getLogger(__name__)


class GetNextSampleUseCase:
    def __init__(
        self, sampling_service: service.SamplingService, unit_of_work: unitofwork.UnitOfWork
    ) -> None:
        self._sampling_service = sampling_service
        self._unit_of_work = unit_of_work

    def execute(self, task_id: model.Id) -> model.Sample | None:
        with self._unit_of_work as unit_of_work:
            unlabeled_samples = unit_of_work.samples.find(
                repository.SampleQuery(has_label=False, task_id=task_id)
            )
            sample_id = self._sampling_service.sample(unlabeled_samples)
            if sample_id is None:
                return None
            sample = unit_of_work.samples.get_by_id(sample_id)
        return sample


class AnnotateSampleUseCase:
    def __init__(self, unit_of_work: unitofwork.UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, sample_id: model.Id, text_class_id: model.Id | None) -> model.Sample:
        with self._unit_of_work as unit_of_work:
            sample = unit_of_work.samples.get_by_id(sample_id)
            if text_class_id is None:
                sample.remove_label()
            else:
                annotation_task = unit_of_work.annotation_tasks.get_by_id(sample.annotation_task_id)
                text_class = annotation_task.get_text_class_by_id(text_class_id)
                sample.annotate(text_class)
            unit_of_work.samples.update(sample)
            unit_of_work.commit()
        return sample


class EmbedAllSamplesUseCase:
    def __init__(
        self, embedding_service: service.EmbeddingService, unit_of_work: unitofwork.UnitOfWork
    ) -> None:
        self._embedding_service = embedding_service
        self._unit_of_work = unit_of_work

    def execute(self) -> bool:
        with self._unit_of_work as unit_of_work:
            samples = unit_of_work.samples.find(repository.SampleQuery(has_embedding=False))
            if len(samples) == 0:
                return False
            embeddings = self._embedding_service.embed_samples(samples)
            for sample, embedding in zip(samples, embeddings):
                sample.embed(embedding)
                unit_of_work.samples.update(sample)
            unit_of_work.commit()
        return True


class EstimateSamplesUseCase:
    def __init__(
        self,
        embedding_aggregation_service: service.EmbeddingAggregationService,
        vector_similarity_service: service.VectorSimilarityService,
        unit_of_work: unitofwork.UnitOfWork,
    ) -> None:
        self._embedding_aggregation_service = embedding_aggregation_service
        self._vector_similarity_service = vector_similarity_service
        self._unit_of_work = unit_of_work

    def execute(self) -> None:
        with self._unit_of_work as unit_of_work:
            class_embeddings = self._calculate_class_embeddings(unit_of_work)
            query = repository.SampleQuery(has_label=True, has_embedding=True)
            samples = unit_of_work.samples.find(query)
            for sample in samples:
                _LOGGER.debug(f"Estimating sample {sample.id}")
                assert sample.embedding is not None
                class_estimates = self._calculate_class_estimates(
                    sample.embedding, class_embeddings
                )
                sample.add_class_estimates(class_estimates)
                unit_of_work.samples.update(sample)
            unit_of_work.commit()

    def _calculate_class_embeddings(
        self, unit_of_work: unitofwork.UnitOfWork
    ) -> dict[str, model.Embedding]:
        samples = unit_of_work.samples.find(
            repository.SampleQuery(has_embedding=True, has_label=True)
        )
        embeddings_by_class: dict[str, list[model.Embedding]] = collections.defaultdict(list)

        for sample in samples:
            assert sample.embedding is not None
            assert sample.text_class is not None
            embeddings_by_class[sample.text_class.id].append(sample.embedding)

        return {
            text_class: self._embedding_aggregation_service.aggregate_embeddings(embeddings)
            for text_class, embeddings in embeddings_by_class.items()
        }

    def _calculate_class_estimates(
        self, sample_embedding: model.Embedding, class_embeddings: dict[str, model.Embedding]
    ) -> tuple[model.ClassEstimate, ...]:
        class_estimates = []
        for text_class, class_embedding in class_embeddings.items():
            similarity = self._vector_similarity_service.calculate_similarity(
                sample_embedding, class_embedding
            )
            class_estimate = model.ClassEstimate.create(
                text_class_id=text_class, confidence=similarity
            )
            class_estimates.append(class_estimate)
        return tuple(class_estimates)
