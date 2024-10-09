"""Test suite for data module."""

import pytest

from nlpanno import data


class TestInMemoryDatabase:
    """Tests for in-memory database."""

    @pytest.fixture
    def database(self):
        """Fixture for the in-memory database."""
        return data.InMemoryDatabase()

    @staticmethod
    def test_add_sample(database: data.Database):
        """Test adding a sample."""
        sample = data.Sample(
            data.create_id(),
            "text",
            None,
        )
        database.add_sample(sample)
        assert len(database.find_samples()) == 1

    @staticmethod
    def test_get_sample_by_id(database: data.Database):
        """Test getting a sample by id."""
        database = data.InMemoryDatabase()
        sample_to_search = data.Sample(
            data.create_id(),
            "text 1",
            "class 1",
        )
        database.add_sample(sample_to_search)
        database.add_sample(
            data.Sample(
                data.create_id(),
                "text 2",
                "class 2",
            )
        )
        assert len(database.find_samples()) == 2
        assert database.get_sample_by_id(sample_to_search.id) == sample_to_search

    @staticmethod
    def test_find_samples(database):
        """Test finding samples."""
        database = data.InMemoryDatabase()
        database.add_sample(
            data.Sample(
                data.create_id(),
                "text 1",
                "class 1",
            )
        )
        database.add_sample(
            data.Sample(
                data.create_id(),
                "text 2",
                "class 1",
            )
        )
        database.add_sample(
            data.Sample(
                data.create_id(),
                "text 3",
                "class 2",
            )
        )
        assert len(database.find_samples()) == 3
        assert len(database.find_samples({"text_class": "class 1"})) == 2
        assert len(database.find_samples({"text_class": "class 2"})) == 1

    @staticmethod
    def test_update(database: data.Database):
        """Test updating a sample."""
        database.add_sample(
            data.Sample(
                data.create_id(),
                "text 1",
                "class 1",
            )
        )

    @staticmethod
    def test_get_task_config_before_set(database: data.Database):
        """Test getting task config fails when not set."""
        with pytest.raises(RuntimeError):
            database.get_task_config()

    @staticmethod
    def test_get_task_config(database: data.Database):
        """Test getting task config succeeds when it is set."""
        task_config = data.TaskConfig(("class 1",))
        database.set_task_config(task_config)
        assert database.get_task_config() == task_config
