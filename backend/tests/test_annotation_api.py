"""Test suite for service."""

import fastapi
import fastapi.testclient
import pytest

import nlpanno.adapters.persistence.inmemory
from nlpanno.adapters import annotation_api
from nlpanno.domain import model

_GET_TASK_ENDPOINT = "/api/tasks/{task_id}"
_PATCH_SAMPLE_ENDPOINT = "/api/samples/{sample_id}"
_NEXT_SAMPLE_ENDPOINT = "/api/tasks/{task_id}/nextSample"

_ANNOTATION_TASK_ID = model.create_id()
_TEXT_CLASS_1 = model.TextClass("c1", "class 1", _ANNOTATION_TASK_ID)
_TEXT_CLASS_2 = model.TextClass("c2", "class 2", _ANNOTATION_TASK_ID)
_ANNOTATION_TASK = model.AnnotationTask(_ANNOTATION_TASK_ID, (_TEXT_CLASS_1, _TEXT_CLASS_2))


def test_get_task() -> None:
    """Test getting the task config."""
    annotation_task = model.AnnotationTask(model.create_id(), (_TEXT_CLASS_1, _TEXT_CLASS_2))
    expected_response = {
        "textClasses": [
            {"id": _TEXT_CLASS_1.id, "name": _TEXT_CLASS_1.name},
            {"id": _TEXT_CLASS_2.id, "name": _TEXT_CLASS_2.name},
        ]
    }
    client = create_client((), annotation_task)
    endpoint = _GET_TASK_ENDPOINT.format(task_id=annotation_task.id)
    response = client.get(endpoint)
    assert response.status_code == 200
    assert response.json() == expected_response


def test_get_next_sample() -> None:
    """Test getting the next sample."""
    sample_id = model.create_id()
    annotation_task_id = model.create_id()
    annotation_task = model.AnnotationTask(annotation_task_id, (_TEXT_CLASS_1, _TEXT_CLASS_2))
    sample = model.Sample(
        id=sample_id,
        annotation_task_id=annotation_task_id,
        text="text",
    )
    client = create_client((sample,), annotation_task)
    endpoint = _NEXT_SAMPLE_ENDPOINT.format(task_id=annotation_task_id)
    response = client.get(endpoint)
    assert response.status_code == 200
    assert response.json() is not None
    assert response.json()["id"] == sample_id


@pytest.mark.parametrize(
    "input_data, expected_response",
    [
        (
            {
                "textClassId": _TEXT_CLASS_2.id,
            },
            {
                "id": "id",
                "text": "text",
                "textClass": {"id": _TEXT_CLASS_2.id, "name": _TEXT_CLASS_2.name},
                "textClassPredictions": [0.0, 0.0],
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
        _ANNOTATION_TASK.id,
        "text",
        _TEXT_CLASS_1,
    )
    client = create_client((sample,), _ANNOTATION_TASK)
    endpoint = _PATCH_SAMPLE_ENDPOINT.format(sample_id=sample.id)
    updated = client.patch(endpoint, json=input_data)
    assert updated.status_code == 200
    assert updated.json() == expected_response


def create_client(
    samples: tuple[model.Sample, ...], task_config: model.AnnotationTask | None = None
) -> fastapi.testclient.TestClient:
    """Create a client for testing."""
    if task_config is None:
        task_config = model.AnnotationTask(model.create_id(), ())

    unit_of_work = nlpanno.adapters.persistence.inmemory.InMemoryUnitOfWork()
    with unit_of_work:
        for sample in samples:
            unit_of_work.samples.create(sample)
        unit_of_work.annotation_tasks.create(task_config)
        unit_of_work.commit()

    app = annotation_api.create_app()
    app.container.unit_of_work.override(unit_of_work)
    return fastapi.testclient.TestClient(app)
