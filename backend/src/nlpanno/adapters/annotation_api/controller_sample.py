"""Implementation of the HTTP endpoints."""

import fastapi
import fastapi.staticfiles
import fastapi.templating

from nlpanno.application import usecase
from . import mapper, requestcontext, schema

router = fastapi.APIRouter(prefix="/samples")


@router.get("/next")
def get_next(
    request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> schema.SampleReadSchema | None:
    """Get the next sample (e.g. for annotation)."""
    unit_of_work = request_context.unit_of_work_factory()
    sample = usecase.get_next_sample(unit_of_work, request_context.sampler)
    if sample is None:
        return None
    return mapper.map_sample_to_read_schema(sample, request_context.task_config)


@router.patch("/{sample_id}")
def patch(
    sample_id: str,
    sample_patch: schema.SamplePatchSchema,
    request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> schema.SampleReadSchema:
    """Patch (partial update) a sample."""
    unit_of_work = request_context.unit_of_work_factory()
    sample = usecase.annotate_sample(unit_of_work, sample_id, sample_patch.text_class)
    return mapper.map_sample_to_read_schema(sample, request_context.task_config)
