"""Test suite for service."""

import fastapi
import fastapi.testclient
from nlpanno import domain
import pytest

from nlpanno import database, sampling, annotation

_SAMPLES_ENDPOINT = "/api/samples"
_TASK_CONFIG_ENDPOINT = "/api/taskConfig"
_NEXT_SAMPLE_ENDPOINT = "/api/nextSample"
_STATUS_ENDPOINT = "/api/status"


def test_get_task_config() -> None:
	"""Test getting the task config."""
	task_config = domain.TaskConfig(("class 1", "class 2"))
	sample_repository = database.InMemorySampleRepository()
	client = create_client(sample_repository, task_config)
	response = client.get(_TASK_CONFIG_ENDPOINT)
	assert response.status_code == 200
	assert response.json() == {"textClasses": ["class 1", "class 2"]}


def test_get_next_sample() -> None:
	"""Test getting the next sample."""
	sample_id = domain.create_id()
	sample_repository = database.InMemorySampleRepository()
	sample_repository.create(domain.Sample(sample_id, "text 1", None))
	client = create_client(sample_repository)
	response = client.get(_NEXT_SAMPLE_ENDPOINT)
	assert response.status_code == 200
	assert response.json()["id"] == sample_id


@pytest.mark.parametrize(
	"input_data, expected_response",
	[
		(
			{
				"textClass": "updated class",
			},
			{
				"id": "id",
				"text": "text",
				"textClass": "updated class",
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
	sample = domain.Sample(
		"id",
		"text",
		"class",
	)
	sample_repository = database.InMemorySampleRepository()
	sample_repository.create(sample)
	client = create_client(sample_repository)
	updated = client.patch(f"{_SAMPLES_ENDPOINT}/{sample.id}", json=input_data)
	assert updated.status_code == 200
	assert updated.json() == expected_response


def create_client(
	sample_repository: database.SampleRepository, task_config: domain.TaskConfig | None = None
) -> fastapi.testclient.TestClient:
	"""Create a client for testing."""
	if task_config is None:
		task_config = domain.TaskConfig(())
	estimation_repository = database.SQLiteEstimationRepository(":memory:")
	app = annotation.create_app(
		sample_repository,
		estimation_repository,
		task_config,
		sampling.RandomSampler(),
		include_static_files=False,
	)
	return fastapi.testclient.TestClient(app)
