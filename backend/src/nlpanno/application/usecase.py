import collections
import logging
from collections.abc import Sequence
from typing import Callable

from nlpanno import domain, sampling
from nlpanno.application import unitofwork

_LOGGER = logging.getLogger(__name__)


EmbeddingFunction = Callable[[Sequence[domain.Sample]], Sequence[domain.Embedding]]
EmbeddingAggregationFunction = Callable[[Sequence[domain.Embedding]], domain.Embedding]
VectorSimilarityFunction = Callable[[domain.Embedding, domain.Embedding], float]

def get_next_sample(unit_of_work: unitofwork.UnitOfWork, sampler: sampling.Sampler) -> domain.Sample | None:
    with unit_of_work:
        unlabeled_samples = unit_of_work.samples.find(domain.SampleQuery(has_label=False))
        sample_id = sampler(unlabeled_samples)
        if sample_id is None:
            return None
        return unit_of_work.samples.get_by_id(sample_id)


def annotate_sample(unit_of_work: unitofwork.UnitOfWork, sample_id: domain.Id, text_class: str | None) -> domain.Sample:
    with unit_of_work:
        sample = unit_of_work.samples.get_by_id(sample_id)
        sample.annotate(text_class)
        unit_of_work.samples.update(sample)
        unit_of_work.commit()
        return sample


def embed_all_samples(unit_of_work: unitofwork.UnitOfWork, embedding_function: EmbeddingFunction) -> bool:
    with unit_of_work:
        samples = unit_of_work.samples.find(domain.SampleQuery(has_embedding=False))
        if len(samples) == 0:
            return False
        embeddings = self._embedding_function(samples)
        for sample, embedding in zip(samples, embeddings):
            sample.embed(embedding)
            unit_of_work.samples.update(sample)
        unit_of_work.commit()
        return True


def estimate_samples(unit_of_work: unitofwork.UnitOfWork, embedding_aggregation_function: EmbeddingAggregationFunction, vector_similarity_function: VectorSimilarityFunction) -> None:
    with unit_of_work:
        class_embeddings = _calculate_class_embeddings(unit_of_work, embedding_aggregation_function)
        query = domain.SampleQuery(has_label=True, has_embedding=True)
        samples = unit_of_work.samples.find(query)
        for sample in samples:
            _LOGGER.debug(f"Estimating sample {sample.id}")
            assert sample.embedding is not None
            class_estimates = _calculate_class_estimates(sample.embedding, class_embeddings)
            sample.add_class_estimates(class_estimates)
            unit_of_work.samples.update(sample)
        unit_of_work.commit()


def _calculate_class_estimates(
    sample_embedding: domain.Embedding,
    class_embeddings: dict[str, domain.Embedding],
    vector_similarity_function: VectorSimilarityFunction,
) -> tuple[domain.ClassEstimate, ...]:
    class_estimates = []
    for text_class, class_embedding in class_embeddings.items():
        similarity = vector_similarity_function(sample_embedding, class_embedding)
        class_estimates.append(domain.ClassEstimate.create(text_class, similarity))
    return tuple(class_estimates)


def _calculate_class_embeddings(
    unit_of_work: unitofwork.UnitOfWork,
    embedding_aggregation_function: EmbeddingAggregationFunction,
) -> dict[str, domain.Embedding]:
    samples = unit_of_work.samples.find(domain.SampleQuery(has_embedding=True, has_label=True))
    embeddings_by_class: dict[str, list[domain.Embedding]] = collections.defaultdict(list)

    for sample in samples:
        assert sample.embedding is not None
        assert sample.text_class is not None
        embeddings_by_class[sample.text_class].append(sample.embedding)

    return {
        text_class: embedding_aggregation_function(embeddings)
        for text_class, embeddings in embeddings_by_class.items()
    }
