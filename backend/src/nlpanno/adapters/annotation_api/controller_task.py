"""Implementation of the HTTP endpoints."""

import fastapi

from nlpanno.application import usecase

from . import mapper, requestcontext, schema

router = fastapi.APIRouter(prefix="/tasks")


@router.get("/{task_id}", response_model=schema.TaskReadSchema)
def get_task(
    task_id: str,
    request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> schema.TaskReadSchema:
    """Get the task config."""
    unit_of_work = request_context.unit_of_work_factory()
    with unit_of_work:
        annotation_task = unit_of_work.annotation_tasks.get_by_id(task_id)
    return mapper.map_task_to_read_schema(annotation_task)


@router.get("/{task_id}/nextSample")
def get_next_sample(
    task_id: str,
    request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> schema.SampleReadSchema | None:
    """Get the next sample (e.g. for annotation)."""
    unit_of_work = request_context.unit_of_work_factory()
    get_next_sample_use_case = usecase.GetNextSampleUseCase(request_context.sampler, unit_of_work)
    sample = get_next_sample_use_case.execute(task_id)
    if sample is None:
        return None
    with unit_of_work:
        annotation_task = unit_of_work.annotation_tasks.get_by_id(task_id)
    return mapper.map_sample_to_read_schema(sample, annotation_task)
