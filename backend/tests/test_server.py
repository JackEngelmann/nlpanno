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


@pytest.mark.parametrize("data, expected_response", [
    (
        {
            "text": "updated text",
        },
        {
            "id": "id",
            "text": "updated text",
            "text_class": "class",
            "text_class_prediction": [0.1, 0.2],
        },
    ),
    (
        {
            "text_class": "updated class",
        },
        {
            "id": "id",
            "text": "text",
            "text_class": "updated class",
            "text_class_prediction": [0.1, 0.2],
        },
    ),
    (
        {
            "text_class": None,
        },
        {
            "id": "id",
            "text": "text",
            "text_class": None,
            "text_class_prediction": [0.1, 0.2],
        },
    ),
    (
        {
            "text_class_prediction": [0.2, 0.3],
        },
        {
            "id": "id",
            "text": "text",
            "text_class": "class",
            "text_class_prediction": [0.2, 0.3],
        },
    ),
    (
        {
            "text_class_prediction": None,
        },
        {
            "id": "id",
            "text": "text",
            "text_class": "class",
            "text_class_prediction": None,
        },
    ),
])
def test_patch_sample(data, expected_response, db: database.Database, test_client: fastapi.testclient.TestClient):
    db.add_sample(
        database.Sample(
            "id",
            "text",
            "class",
            [0.1, 0.2],
        )
    )
    updated = test_client.patch(f'/samples/id', json=data)
    assert updated.status_code == 200
    assert updated.json() == expected_response



@pytest.fixture()
def db():
    return database.InMemoryDatabase()


@pytest.fixture
def test_client(db):
    app = server.create_app(1, db)
    return fastapi.testclient.TestClient(app)