from nlpanno import database
import pytest


class TestInMemoryDatabase:
    @pytest.fixture
    def db(self):
        return database.InMemoryDatabase()

    @staticmethod
    def test_add_sample(db: database.Database):
        sample = database.Sample(
            database.create_id(),
            "text",
            None,
        )
        db.add_sample(sample)
        assert len(db.find_samples()) == 1


    @staticmethod
    def test_get_sample_by_id(db: database.Database):
        db = database.InMemoryDatabase()
        sample_to_search = database.Sample(
            database.create_id(),
            "text 1",
            "class 1",
        )
        db.add_sample(sample_to_search)
        db.add_sample(database.Sample(
            database.create_id(),
            "text 2",
            "class 2",
        ))
        assert len(db.find_samples()) == 2
        assert db.get_sample_by_id(sample_to_search.id) == sample_to_search


    @staticmethod
    def test_find_samples(db):
        db = database.InMemoryDatabase()
        db.add_sample(
            database.Sample(
                database.create_id(),
                "text 1",
                "class 1",
            )
        )
        db.add_sample(
            database.Sample(
                database.create_id(),
                "text 2",
                "class 1",
            )
        )
        db.add_sample(
            database.Sample(
                database.create_id(),
                "text 3",
                "class 2",
            )
        )
        assert len(db.find_samples()) == 3
        assert len(db.find_samples({ "text_class": "class 1"})) == 2
        assert len(db.find_samples({ "text_class": "class 2"})) == 1
    
    @staticmethod
    def test_update(db: database.Database):
        db.add_sample(
            database.Sample(
                database.create_id(),
                "text 1",
                "class 1",
            )
        )

    @staticmethod
    def test_get_task_config_before_set(db: database.Database):
        with pytest.raises(RuntimeError):
            db.get_task_config()

    @staticmethod
    def test_get_task_config(db: database.Database):
        task_config = database.TaskConfig(['class 1'])
        db.set_task_config(task_config)
        assert db.get_task_config() == task_config

