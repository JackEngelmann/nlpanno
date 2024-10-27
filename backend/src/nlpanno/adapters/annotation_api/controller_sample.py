"""Implementation of the HTTP endpoints."""

import fastapi
from dependency_injector.wiring import Provide, inject

from nlpanno.application import usecase
from nlpanno.container import Container

from . import mapper, schema

router = fastapi.APIRouter(prefix="/samples")


@router.patch("/{sample_id}")
@inject
def patch(
    sample_id: str,
    sample_patch: schema.SamplePatchSchema,
    annotate_sample_use_case: usecase.AnnotateSampleUseCase = fastapi.Depends(  # noqa: B008
        Provide[Container.annotate_sample_use_case]
    ),
    fetch_annotation_task_use_case: usecase.FetchAnnotationTaskUseCase = fastapi.Depends(  # noqa: B008
        Provide[Container.fetch_annotation_task_use_case]
    ),
) -> schema.SampleReadSchema:
    """Patch (partial update) a sample."""
    sample = annotate_sample_use_case.execute(sample_id, sample_patch.text_class_id)
    annotation_task = fetch_annotation_task_use_case.execute(sample.annotation_task_id)
    return mapper.map_sample_to_read_schema(sample, annotation_task)
