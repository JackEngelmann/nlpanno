"""Test suite for service."""

import fastapi
import fastapi.testclient
import pytest

from nlpanno import data, sampling, server


_SAMPLES_ENDPOINT = "/api/samples"
_TASK_CONFIG_ENDPOINT = "/api/taskConfig"
_NEXT_SAMPLE_ENDPOINT = "/api/nextSample"
_STATUS_ENDPOINT = "/api/status"


def test_get_samples() -> None:
	"""Test getting samples."""
	samples = [
		data.Sample(data.create_id(), "text 1", None),
		data.Sample(data.create_id(), "text 2", None),
	]
	database = data.InMemoryDatabase(samples)
	client = create_client(database)
	response = client.get(_SAMPLES_ENDPOINT)
	assert response.status_code == 200
	assert len(response.json()) == len(samples)


def test_get_next_sample() -> None:
	"""Test getting the next sample."""
	sample_id = data.create_id()
	database = data.InMemoryDatabase((data.Sample(sample_id, "text 1", None),))
	client = create_client(database)
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
) -> None:
	"""Test the patching (partial update) a sample."""
	sample = data.Sample(
		"id",
		"text",
		"class",
		(0.1, 0.2),
	)
	database = data.InMemoryDatabase((sample,))
	client = create_client(database)
	updated = client.patch(f"{_SAMPLES_ENDPOINT}/{sample.id}", json=input_data)
	assert updated.status_code == 200
	assert updated.json() == expected_response


def test_get_status() -> None:
	"""Test getting the status of the server."""
	database = data.InMemoryDatabase(())
	client = create_client(database)
	response = client.get(_STATUS_ENDPOINT)
	assert response.status_code == 200
	assert response.json()["worker"]["isWorking"] is False


def create_client(database: data.Database) -> fastapi.testclient.TestClient:
	"""Create a client for testing."""
	app = server.create_app(
		database,
		data.TaskConfig(()),
		sampling.RandomSampler(),
		lambda: None,
	)
	return fastapi.testclient.TestClient(app)


@pytest.fixture
def client(database: data.Database) -> fastapi.testclient.TestClient:
	"""Fixture for fastAPI test client."""
	app = server.create_app(
		database,
		sampling.RandomSampler(),
		lambda: None,
	)
	return fastapi.testclient.TestClient(app)
