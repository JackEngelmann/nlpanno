"""Test suite for data module."""

from collections.abc import Generator

from nlpanno import domain
import pytest
import torch

from nlpanno import database


class TestSampleRepository:
	"""Test suite for the sample repository."""

	@staticmethod
	def test_get_by_id(sample_repository: database.SampleRepository) -> None:
		"""Test getting a sample by id."""
		sample_to_find = domain.Sample(
			domain.create_id(),
			"text 1",
			"class 1",
		)
		other_sample = domain.Sample(
			domain.create_id(),
			"text 2",
			"class 2",
		)
		sample_repository.create(sample_to_find)
		sample_repository.create(other_sample)
		found_sample = sample_repository.get_by_id(sample_to_find.id)
		assert found_sample is not None
		assert found_sample == sample_to_find

	@staticmethod
	def test_get_all(sample_repository: database.SampleRepository) -> None:
		"""Test finding samples."""
		samples = (
			domain.Sample(
				domain.create_id(),
				"text 1",
				"class 1",
			),
			domain.Sample(
				domain.create_id(),
				"text 2",
				"class 1",
			),
			domain.Sample(
				domain.create_id(),
				"text 3",
				"class 2",
			),
		)
		for sample in samples:
			sample_repository.create(sample)
		assert len(sample_repository.get_all()) == len(samples)

	@staticmethod
	def test_update(sample_repository: database.SampleRepository) -> None:
		"""Test updating a sample."""
		sample_to_update = domain.Sample(
			domain.create_id(),
			"text 1",
			"class 1",
		)
		sample_repository.create(sample_to_update)
		updated_sample = domain.Sample(
			sample_to_update.id,
			"updated text",
			"class 2",
		)
		sample_repository.update(updated_sample)
		assert sample_repository.get_by_id(sample_to_update.id) == updated_sample

	@staticmethod
	def test_get_unlabeled(sample_repository: database.SampleRepository) -> None:
		"""Test getting unlabeled samples."""
		unlabeled_id = domain.create_id()
		sample_repository.create(
			domain.Sample(domain.create_id(), "text 1", "class 1"),
		)
		sample_repository.create(
			domain.Sample(unlabeled_id, "text 2", None),
		)
		unlabeled_samples = sample_repository.get_unlabeled()
		assert len(unlabeled_samples) == 1
		assert unlabeled_samples[0].id == unlabeled_id


class TestEmbeddingRepository:
	"""Test suite for the embedding repository."""

	@staticmethod
	def test_create(embedding_repository: database.EmbeddingRepository) -> None:
		"""Test creating an embedding."""
		embedding_repository.create(domain.SampleEmbedding("sample_id", torch.rand(10)))

	@staticmethod
	def test_get(embedding_repository: database.EmbeddingRepository) -> None:
		"""Test getting an embedding."""
		embedding = torch.rand(10)
		id_ = domain.create_id()
		embedding_repository.create(domain.SampleEmbedding(id_, embedding))
		queried_sample_embedding = embedding_repository.get(id_)
		assert queried_sample_embedding is not None
		assert queried_sample_embedding.sample_id == id_
		assert torch.allclose(queried_sample_embedding.embedding, embedding)

	@staticmethod
	def test_has(embedding_repository: database.EmbeddingRepository) -> None:
		"""Test checking if an embedding exists."""
		embedding_repository.create(domain.SampleEmbedding("sample_id", torch.rand(10)))
		assert embedding_repository.has("sample_id")
		assert not embedding_repository.has(domain.create_id())


class TestEstimationRepository:
	"""Test suite for the estimation repository."""

	@staticmethod
	def test_get_sample_estimates(estimation_repository: database.EstimationRepository) -> None:
		"""Test getting estimations for a sample."""
		estimation_repository.add_or_update(domain.Estimate("sample_id", "text_class", 0.5))
		assert estimation_repository.get_by_sample_id("sample_id") == (
			domain.Estimate("sample_id", "text_class", 0.5),
		)

	@staticmethod
	def test_add_or_update(estimation_repository: database.EstimationRepository) -> None:
		"""Test adding an estimation."""
		estimation_repository.add_or_update(domain.Estimate("sample_id", "a", 0.1))
		estimation_repository.add_or_update(domain.Estimate("sample_id", "b", 0.2))
		estimation_repository.add_or_update(domain.Estimate("sample_id", "c", 0.3))
		estimation_repository.add_or_update(domain.Estimate("sample_id", "b", 0.4))

		estimates = estimation_repository.get_by_sample_id("sample_id")
		assert len(estimates) == 3
		a_estimate = next(e for e in estimates if e.text_class == "a")
		assert a_estimate.confidence == 0.1
		b_estimate = next(e for e in estimates if e.text_class == "b")
		assert b_estimate.confidence == 0.4
		c_estimate = next(e for e in estimates if e.text_class == "c")
		assert c_estimate.confidence == 0.3


@pytest.fixture(params=("inmemory", "sqlite"))
def sample_repository(
	request: pytest.FixtureRequest,
) -> Generator[database.SampleRepository, None, None]:
	"""Sample repository fixture."""
	if request.param == "inmemory":
		yield database.InMemorySampleRepository()
	if request.param == "sqlite":
		with database.SQLiteSampleRepository(":memory:") as repository:
			yield repository


@pytest.fixture
def embedding_repository() -> Generator[database.EmbeddingRepository, None, None]:
	"""Embedding repository fixture."""
	with database.SQLiteEmbeddingRepository(":memory:") as repository:
		yield repository


@pytest.fixture
def estimation_repository() -> Generator[database.EstimationRepository, None, None]:
	"""Estimation repository fixture."""
	with database.SQLiteEstimationRepository(":memory:") as repository:
		yield repository
