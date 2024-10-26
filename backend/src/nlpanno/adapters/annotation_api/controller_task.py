"""Implementation of the HTTP endpoints."""

import fastapi

from . import mapper, requestcontext, schema

router = fastapi.APIRouter(prefix="/tasks")


@router.get("/", response_model=schema.TaskReadSchema)
def get_task_config(
    request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> schema.TaskReadSchema:
    """Get the task config."""
    return mapper.map_task_to_read_schema(request_context.task_config)
