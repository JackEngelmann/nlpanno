"""Implementation of the HTTP endpoints."""

import fastapi
from dependency_injector.wiring import Provide, inject

from nlpanno.application import usecase
from nlpanno.container import Container

from . import mapper, schema

router = fastapi.APIRouter(prefix="/tasks")


@router.get("/{task_id}", response_model=schema.TaskReadSchema)
@inject
def get_task(
    task_id: str,
    fetch_annotation_task_use_case: usecase.FetchAnnotationTaskUseCase = fastapi.Depends(  # noqa: B008
        Provide[Container.fetch_annotation_task_use_case]
    ),
) -> schema.TaskReadSchema:
    """Get the task config."""
    annotation_task = fetch_annotation_task_use_case.execute(task_id)
    return mapper.map_task_to_read_schema(annotation_task)


@router.get("", response_model=list[schema.TaskReadSchema])
@inject
def get_tasks(
    fetch_all_annotation_tasks_use_case: usecase.FetchAllAnnotationTasksUseCase = fastapi.Depends(  # noqa: B008
        Provide[Container.fetch_all_annotation_tasks_use_case]
    ),
) -> list[schema.TaskReadSchema]:
    """Get all tasks."""
    annotation_tasks = fetch_all_annotation_tasks_use_case.execute()
    return [mapper.map_task_to_read_schema(task) for task in annotation_tasks]


@router.get("/{task_id}/nextSample")
@inject
def get_next_sample(
    task_id: str,
    fetch_annotation_task_use_case: usecase.FetchAnnotationTaskUseCase = fastapi.Depends(  # noqa: B008
        Provide[Container.fetch_annotation_task_use_case]
    ),
    get_next_sample_use_case: usecase.GetNextSampleUseCase = fastapi.Depends(  # noqa: B008
        Provide[Container.get_next_sample_use_case]
    ),
) -> schema.SampleReadSchema | None:
    """Get the next sample (e.g. for annotation)."""
    sample = get_next_sample_use_case.execute(task_id)
    if sample is None:
        return None
    annotation_task = fetch_annotation_task_use_case.execute(task_id)
    return mapper.map_sample_to_read_schema(sample, annotation_task)
