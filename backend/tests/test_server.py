"""Test suite for service."""

import fastapi
import fastapi.testclient
import pytest

from nlpanno import data, sampling, server


_SAMPLES_ENDPOINT = "/api/samples"
_TASK_CONFIG_ENDPOINT = "/api/taskConfig"
_NEXT_SAMPLE_ENDPOINT = "/api/nextSample"
_STATUS_ENDPOINT = "/api/status"


def test_get_samples(database: data.Database, client: fastapi.testclient.TestClient) -> None:
	"""Test getting samples."""
	samples = [
		data.Sample(data.create_id(), "text 1", None),
		data.Sample(data.create_id(), "text 2", None),
	]
	for sample in samples:
		database.add_sample(sample)
	response = client.get(_SAMPLES_ENDPOINT)
	assert response.status_code == 200
	assert len(response.json()) == len(samples)


def get_task_config(database: data.Database, client: fastapi.testclient.TestClient) -> None:
	"""Test getting the task config."""
	task_config = data.TaskConfig(("class 1", "class 2"))
	database.set_task_config(task_config)
	response = client.get(_TASK_CONFIG_ENDPOINT)
	assert response.status_code == 200
	assert response.json()["textClasses"] == ["class 1", "class 2"]


def test_get_next_sample(database: data.Database, client: fastapi.testclient.TestClient) -> None:
	"""Test getting the next sample."""
	sample_id = data.create_id()
	database.add_sample(data.Sample(sample_id, "text 1", None))
	response = client.get(_NEXT_SAMPLE_ENDPOINT)
	assert response.status_code == 200
	assert response.json()["id"] == sample_id


@pytest.mark.parametrize(
	"input_data, expected_response",
	[
		(
			{
				"text": "updated text",
			},
			{
				"id": "id",
				"text": "updated text",
				"textClass": "class",
				"textClassPredictions": [0.1, 0.2],
			},
		),
		(
			{
				"textClass": "updated class",
			},
			{
				"id": "id",
				"text": "text",
				"textClass": "updated class",
				"textClassPredictions": [0.1, 0.2],
			},
		),
		(
			{
				"textClass": None,
			},
			{
				"id": "id",
				"text": "text",
				"textClass": None,
				"textClassPredictions": [0.1, 0.2],
			},
		),
		(
			{
				"textClassPredictions": [0.2, 0.3],
			},
			{
				"id": "id",
				"text": "text",
				"textClass": "class",
				"textClassPredictions": [0.2, 0.3],
			},
		),
		(
			{
				"textClassPredictions": None,
			},
			{
				"id": "id",
				"text": "text",
				"textClass": "class",
				"textClassPredictions": None,
			},
		),
	],
)
def test_patch_sample(
	input_data: dict,
	expected_response: dict,
	database: data.Database,
	client: fastapi.testclient.TestClient,
) -> None:
	"""Test the patching (partial update) a sample."""
	sample = data.Sample(
		"id",
		"text",
		"class",
		(0.1, 0.2),
	)
	database.add_sample(sample)
	updated = client.patch(f"{_SAMPLES_ENDPOINT}/{sample.id}", json=input_data)
	assert updated.status_code == 200
	assert updated.json() == expected_response


def test_get_status(database: data.Database, client: fastapi.testclient.TestClient) -> None:
	"""Test getting the status of the server."""
	response = client.get(_STATUS_ENDPOINT)
	assert response.status_code == 200
	assert response.json()["worker"]["isWorking"] is False


@pytest.fixture()
def database() -> data.Database:
	"""Fixture for an (in-memory) database."""
	return data.InMemoryDatabase()


@pytest.fixture
def client(database: data.Database) -> fastapi.testclient.TestClient:
	"""Fixture for fastAPI test client."""
	app = server.create_app(
		database,
		sampling.RandomSampler(),
		lambda: None,
	)
	return fastapi.testclient.TestClient(app)
