"""Implementation of the HTTP endpoints."""

import fastapi
import fastapi.staticfiles
import fastapi.templating

from nlpanno.application import usecase

from . import mapper, requestcontext, schema

router = fastapi.APIRouter(prefix="/samples")


@router.patch("/{sample_id}")
def patch(
    sample_id: str,
    sample_patch: schema.SamplePatchSchema,
    request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> schema.SampleReadSchema:
    """Patch (partial update) a sample."""
    unit_of_work = request_context.unit_of_work_factory()
    annotate_sample_use_case = usecase.AnnotateSampleUseCase(unit_of_work)
    sample = annotate_sample_use_case.execute(sample_id, sample_patch.text_class_id)
    with unit_of_work:
        annotation_task = unit_of_work.annotation_tasks.get_by_id(sample.annotation_task_id)
    return mapper.map_sample_to_read_schema(sample, annotation_task)
