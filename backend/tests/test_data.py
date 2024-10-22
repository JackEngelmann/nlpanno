"""Test suite for data module."""

import pytest

from nlpanno import data


class TestInMemoryDatabase:
	"""Tests for in-memory database."""

	@staticmethod
	def test_get_sample_by_id() -> None:
		"""Test getting a sample by id."""
		task_config = data.TaskConfig(("class 1", "class 2"))
		sample_to_find = data.Sample(
			data.create_id(),
			"text 1",
			"class 1",
		)
		other_sample = data.Sample(
			data.create_id(),
			"text 2",
			"class 2",
		)
		database = data.InMemoryDatabase(task_config, (sample_to_find, other_sample))
		assert len(database.find_samples()) == 2
		found_sample = database.get_sample_by_id(sample_to_find.id)
		assert found_sample is not None
		assert found_sample == sample_to_find

	@staticmethod
	def test_find_samples() -> None:
		"""Test finding samples."""
		task_config = data.TaskConfig(("class 1", "class 2"))
		samples = (
			data.Sample(
				data.create_id(),
				"text 1",
				"class 1",
			),
			data.Sample(
				data.create_id(),
				"text 2",
				"class 1",
			),
			data.Sample(
				data.create_id(),
				"text 3",
				"class 2",
			),
		)
		database = data.InMemoryDatabase(task_config, samples)
		assert len(database.find_samples()) == 3
		assert len(database.find_samples({"text_class": "class 1"})) == 2
		assert len(database.find_samples({"text_class": "class 2"})) == 1

	@staticmethod
	def test_update() -> None:
		"""Test updating a sample."""
		task_config = data.TaskConfig(("class 1", "class 2"))
		sample_to_update = data.Sample(
			data.create_id(),
			"text 1",
			"class 1",
		)
		database = data.InMemoryDatabase(task_config, (sample_to_update,))
		updated_sample = data.Sample(
			sample_to_update.id,
			"updated text",
			"class 2",
		)
		database.update_sample(updated_sample)
		assert database.get_sample_by_id(sample_to_update.id) == updated_sample

	@staticmethod
	def test_get_task_config() -> None:
		"""Test getting task config succeeds when it is set."""
		task_config = data.TaskConfig(("class 1",))
		database = data.InMemoryDatabase(task_config, ())
		assert database.get_task_config() == task_config
