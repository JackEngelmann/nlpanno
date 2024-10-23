"""Test suite for data module."""

from nlpanno import data, domain


class TestInMemoryDatabase:
	"""Tests for in-memory database."""

	@staticmethod
	def test_get_sample_by_id() -> None:
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
		database = data.InMemoryDatabase((sample_to_find, other_sample))
		assert len(database.get_all_samples()) == 2
		found_sample = database.get_sample_by_id(sample_to_find.id)
		assert found_sample is not None
		assert found_sample == sample_to_find

	@staticmethod
	def test_find_samples() -> None:
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
		database = data.InMemoryDatabase(samples)
		assert len(database.get_all_samples()) == 3

	@staticmethod
	def test_update() -> None:
		"""Test updating a sample."""
		sample_to_update = domain.Sample(
			domain.create_id(),
			"text 1",
			"class 1",
		)
		database = data.InMemoryDatabase((sample_to_update,))
		updated_sample = domain.Sample(
			sample_to_update.id,
			"updated text",
			"class 2",
		)
		database.update_sample(updated_sample)
		assert database.get_sample_by_id(sample_to_update.id) == updated_sample
	
	@staticmethod
	def test_get_unlabeled_samples() -> None:
		"""Test getting unlabeled samples."""
		unlabeled_id = domain.create_id()
		samples = (
			domain.Sample(domain.create_id(), "text 1", "class 1"),
			domain.Sample(unlabeled_id, "text 2", None),
		)
		database = data.InMemoryDatabase(samples)
		unlabeled_samples = database.get_unlabeled_samples()
		assert len(unlabeled_samples) == 1
		assert unlabeled_samples[0].id == unlabeled_id
