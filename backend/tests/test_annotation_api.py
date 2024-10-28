"""Test suite for service."""

import fastapi
import fastapi.testclient

import nlpanno.adapters.persistence.inmemory
from nlpanno.adapters import annotation_api
from nlpanno.domain import model

_GET_TASK_ENDPOINT = "/api/tasks/{task_id}"
_GET_TASKS_ENDPOINT = "/api/tasks"
_PATCH_SAMPLE_ENDPOINT = "/api/samples/{sample_id}"
_NEXT_SAMPLE_ENDPOINT = "/api/tasks/{task_id}/nextSample"


def test_get_task() -> None:
    """Test getting the task config."""
    annotation_task = model.AnnotationTask.create()
    text_class = annotation_task.create_text_class("class name")
    expected_response = {
        "id": annotation_task.id,
        "textClasses": [
            {"id": text_class.id, "name": text_class.name},
        ],
    }
    client = create_client((), annotation_task)
    endpoint = _GET_TASK_ENDPOINT.format(task_id=annotation_task.id)

    response = client.get(endpoint)

    assert response.status_code == 200
    assert response.json() == expected_response


def test_get_tasks() -> None:
    """Test getting all tasks."""
    annotation_task = model.AnnotationTask.create()
    text_class = annotation_task.create_text_class("class name")
    client = create_client((), annotation_task)

    response = client.get(_GET_TASKS_ENDPOINT)

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": annotation_task.id,
            "textClasses": [{"id": text_class.id, "name": text_class.name}],
        }
    ]


def test_get_next_sample() -> None:
    """Test getting the next sample."""
    annotation_task = model.AnnotationTask.create()
    text_class_1 = annotation_task.create_text_class("class 1")
    text_class_2 = annotation_task.create_text_class("class 2")
    sample = model.Sample.create(annotation_task.id, "text")
    sample.add_class_estimate(model.ClassEstimate.create(text_class_1.id, 0.2))
    sample.add_class_estimate(model.ClassEstimate.create(text_class_2.id, 0.3))
    expected_response = {
        "id": sample.id,
        "text": "text",
        "textClass": None,
        "availableTextClasses": [
            {"id": text_class_2.id, "name": text_class_2.name, "confidence": 0.3},
            {"id": text_class_1.id, "name": text_class_1.name, "confidence": 0.2},
        ],
    }
    client = create_client((sample,), annotation_task)
    endpoint = _NEXT_SAMPLE_ENDPOINT.format(task_id=annotation_task.id)

    response = client.get(endpoint)

    assert response.status_code == 200
    assert response.json() == expected_response


def test_patch_sample() -> None:
    """Test the patching (partial update) a sample."""
    annotation_task = model.AnnotationTask.create()
    text_class_1 = annotation_task.create_text_class("class 1")
    text_class_2 = annotation_task.create_text_class("class 2")
    sample = model.Sample.create(annotation_task.id, "text")
    sample.annotate(text_class_1)
    client = create_client((sample,), annotation_task)
    endpoint = _PATCH_SAMPLE_ENDPOINT.format(sample_id=sample.id)
    input_data = {"textClassId": text_class_2.id}

    updated = client.patch(endpoint, json=input_data)

    assert updated.status_code == 200
    assert updated.json()["textClass"]["id"] == text_class_2.id


def create_client(
    samples: tuple[model.Sample, ...], task_config: model.AnnotationTask
) -> fastapi.testclient.TestClient:
    """Create a client for testing."""
    unit_of_work = nlpanno.adapters.persistence.inmemory.InMemoryUnitOfWork()
    with unit_of_work:
        for sample in samples:
            unit_of_work.samples.create(sample)
        unit_of_work.annotation_tasks.create(task_config)
        unit_of_work.commit()

    app = annotation_api.create_app()
    app.container.unit_of_work.override(unit_of_work)  # type: ignore
    return fastapi.testclient.TestClient(app)
