from os import stat
from nlpanno import database
import pytest


class TestInMemoryDatabase:
    @pytest.fixture
    def db(self):
        return database.InMemoryDatabase()

    @staticmethod
    def test_add(db):
        sample = database.Sample(
            database.create_id(),
            "text",
            None,
        )
        db.add(sample)
        assert len(db.find_all()) == 1


    @staticmethod
    def test_get_id(db):
        db = database.InMemoryDatabase()
        sample_to_search = database.Sample(
            database.create_id(),
            "text 1",
            "class 1",
        )
        db.add(sample_to_search)
        db.add(database.Sample(
            database.create_id(),
            "text 2",
            "class 2",
        ))
        assert len(db.find_all()) == 2
        assert db.get_id(sample_to_search.id) == sample_to_search


    @staticmethod
    def test_find_all(db):
        db = database.InMemoryDatabase()
        db.add(
            database.Sample(
                database.create_id(),
                "text 1",
                "class 1",
            )
        )
        db.add(
            database.Sample(
                database.create_id(),
                "text 2",
                "class 1",
            )
        )
        db.add(
            database.Sample(
                database.create_id(),
                "text 3",
                "class 2",
            )
        )
        assert len(db.find_all()) == 3
        assert len(db.find_all({ "text_class": "class 1"})) == 2
        assert len(db.find_all({ "text_class": "class 2"})) == 1
    
    @staticmethod
    def test_update(db):
        db.add(
            database.Sample(
                database.create_id(),
                "text 1",
                "class 1",
            )
        )
