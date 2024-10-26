"""Test suite for service."""

import fastapi
import fastapi.testclient
import pytest

import nlpanno.adapters.persistence.inmemory
from nlpanno import sampling
from nlpanno.adapters.annotation_api import main
from nlpanno.domain import model

_SAMPLES_ENDPOINT = "/api/samples"
_TASK_ENDPOINT = "/api/tasks"
_NEXT_SAMPLE_ENDPOINT = "/api/samples/next"


def test_get_task_config() -> None:
    """Test getting the task config."""
    task_config = model.AnnotationTask(("class 1", "class 2"))
    client = create_client((), task_config)
    response = client.get(_TASK_ENDPOINT)
    assert response.status_code == 200
    assert response.json() == {"textClasses": ["class 1", "class 2"]}


def test_get_next_sample() -> None:
    """Test getting the next sample."""
    sample_id = model.create_id()
    sample = model.Sample(sample_id, "text 1", None)
    client = create_client((sample,))
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
                "textClassPredictions": [],
            },
        ),
    ],
)
def test_patch_sample(
    input_data: dict,
    expected_response: dict,
) -> None:
    """Test the patching (partial update) a sample."""
    sample = model.Sample(
        "id",
        "text",
        "class",
    )
    client = create_client((sample,))
    updated = client.patch(f"{_SAMPLES_ENDPOINT}/{sample.id}", json=input_data)
    assert updated.status_code == 200
    assert updated.json() == expected_response


def create_client(
    samples: tuple[model.Sample, ...], task_config: model.AnnotationTask | None = None
) -> fastapi.testclient.TestClient:
    """Create a client for testing."""
    if task_config is None:
        task_config = model.AnnotationTask(())

    unit_of_work_factory = nlpanno.adapters.persistence.inmemory.InMemoryUnitOfWorkFactory()
    with unit_of_work_factory() as unit_of_work:
        for sample in samples:
            unit_of_work.samples.create(sample)
        unit_of_work.commit()

    app = main.create_app(
        unit_of_work_factory,
        task_config,
        sampling.RandomSampler(),
        include_static_files=False,
    )
    return fastapi.testclient.TestClient(app)
