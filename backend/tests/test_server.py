import fastapi
import fastapi.testclient
from nlpanno import database, sampling, server
import pytest


def test_get_samples(db: database.Database, test_client: fastapi.testclient.TestClient):
    samples = [
        database.Sample(
            database.create_id(),
            "text 1",
            None
        ),
        database.Sample(
            database.create_id(),
            "text 2",
            None
        )
    ]
    for sample in samples:
        db.add_sample(sample)
    response = test_client.get('/samples')
    assert response.status_code == 200
    assert len(response.json()) == len(samples)


def test_get_next_sample(db: database.Database, test_client: fastapi.testclient.TestClient):
    sample_id = database.create_id()
    db.add_sample(
        database.Sample(
            sample_id,
            "text 1",
            None
        )
    )
    response = test_client.get('/nextSample')
    assert response.status_code == 200
    assert response.json()['id'] == sample_id



@pytest.fixture()
def db():
    return database.InMemoryDatabase()


@pytest.fixture
def test_client(db):
    app = server.create_app(1, db)
    return fastapi.testclient.TestClient(app)