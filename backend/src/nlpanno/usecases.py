import abc
import collections
import logging
from collections.abc import Sequence
from typing import Callable
from dataclasses import dataclass

from nlpanno import domain, sampling

_LOGGER = logging.getLogger(__name__)


EmbeddingFunction = Callable[[Sequence[domain.Sample]], Sequence[domain.Embedding]]
EmbeddingAggregationFunction = Callable[[Sequence[domain.Embedding]], domain.Embedding]
VectorSimilarityFunction = Callable[[domain.Embedding, domain.Embedding], float]


@dataclass
class SampleQuery:
    """Query for finding samples."""

    has_label: bool | None = None
    has_embedding: bool | None = None


class SampleRepository(abc.ABC):
    """Base class for all sample repositories."""

    @abc.abstractmethod
    def get_by_id(self, id_: domain.Id) -> domain.Sample:
        """Get a sample by the unique identifier."""
        raise NotImplementedError()

    @abc.abstractmethod
    def find(self, query: SampleQuery | None = None) -> tuple[domain.Sample, ...]:
        """Find samples by the given query."""
        raise NotImplementedError()

    @abc.abstractmethod
    def update(self, sample: domain.Sample) -> None:
        """Update a sample."""
        raise NotImplementedError()

    @abc.abstractmethod
    def create(self, sample: domain.Sample) -> None:
        """Create a sample."""
        raise NotImplementedError()


class GetNextSampleUseCase:
    """Usecase for getting the next sample for annotation."""

    def __init__(self, sample_repository: SampleRepository, sampler: sampling.Sampler) -> None:
        self._sample_repository = sample_repository
        self._sampler = sampler

    def __call__(self) -> domain.Sample | None:
        """Get the next sample for annotation."""
        unlabeled_samples = self._sample_repository.find(SampleQuery(has_label=False))
        sample_id = self._sampler(unlabeled_samples)
        if sample_id is None:
            return None
        return self._sample_repository.get_by_id(sample_id)


class AnnotateSampleUseCase:
    """Usecase for annotating a sample."""

    def __init__(self, sample_repository: SampleRepository) -> None:
        self._sample_repository = sample_repository

    def __call__(self, sample_id: domain.Id, text_class: str | None) -> domain.Sample:
        """Annotate a sample."""
        sample = self._sample_repository.get_by_id(sample_id)
        sample.annotate(text_class)
        self._sample_repository.update(sample)
        return sample


class EmbedAllSamplesUseCase:
    """Usecase for embedding all samples."""

    def __init__(
        self, sample_repository: SampleRepository, embedding_function: EmbeddingFunction
    ) -> None:
        self._sample_repository = sample_repository
        self._embedding_function = embedding_function

    def __call__(self) -> bool:
        """Embed all samples."""
        samples = self._sample_repository.find(SampleQuery(has_embedding=False))
        if len(samples) == 0:
            return False
        embeddings = self._embedding_function(samples)
        for sample, embedding in zip(samples, embeddings):
            sample.embed(embedding)
            self._sample_repository.update(sample)
        return True


class EstimateSamplesUseCase:
    """Usecase for estimating samples."""

    def __init__(
        self,
        sample_repository: SampleRepository,
        embedding_aggregation_function: EmbeddingAggregationFunction,
        vector_similarity_function: VectorSimilarityFunction,
    ) -> None:
        self._sample_repository = sample_repository
        self._embedding_aggregation_function = embedding_aggregation_function
        self._vector_similarity_function = vector_similarity_function

    def __call__(self) -> None:
        """Estimate samples."""
        class_embeddings = self._calculate_class_embeddings()
        unlabeled_samples = self._sample_repository.get_unlabeled()
        for sample in unlabeled_samples:
            if sample.embedding is None:
                continue
            _LOGGER.debug(f"Estimating sample {sample.id}")
            class_estimates = self._calculate_class_estimates(sample.embedding, class_embeddings)
            sample.add_class_estimates(class_estimates)
            self._sample_repository.update(sample)

    def _calculate_class_estimates(
        self, sample_embedding: domain.Embedding, class_embeddings: dict[str, domain.Embedding]
    ) -> tuple[domain.ClassEstimate, ...]:
        class_estimates = []
        for text_class, class_embedding in class_embeddings.items():
            similarity = self._vector_similarity_function(sample_embedding, class_embedding)
            class_estimates.append(domain.ClassEstimate.create(text_class, similarity))
        return tuple(class_estimates)

    def _calculate_class_embeddings(self) -> dict[str, domain.Embedding]:
        samples = self._sample_repository.find(SampleQuery(has_embedding=True, has_label=True))

        embeddings_by_class: dict[str, list[domain.Embedding]] = collections.defaultdict(list)
        for sample in samples:
            embeddings_by_class[sample.text_class].append(sample.embedding)

        return {
            text_class: self._embedding_aggregation_function(embeddings)
            for text_class, embeddings in embeddings_by_class.items()
        }
