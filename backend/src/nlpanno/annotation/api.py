"""Implementation of the HTTP endpoints."""

import fastapi
import fastapi.staticfiles
import fastapi.templating

from nlpanno.application import usecase
from nlpanno.annotation import requestcontext, transferobject, types

router = fastapi.APIRouter(prefix="/api")


@router.get("/taskConfig", response_model=transferobject.TaskConfigDTO)
def get_task_config(
    request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> transferobject.TaskConfigDTO:
    """Get the task config."""
    return transferobject.TaskConfigDTO.from_domain_object(request_context.task_config)


@router.get("/nextSample")
def get_next_sample(
    request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> transferobject.SampleDTO | None:
    """Get the next sample (e.g. for annotation)."""
    with request_context.session_factory() as session:
        use_case = usecase.GetNextSampleUseCase(session.sample_repository, request_context.sampler)
        sample = use_case()
    if sample is None:
        return None

    # TODO: refactor to use usecase or DTO.
    confidence_by_class = {
        estimate.text_class: estimate.confidence for estimate in sample.estimates
    }
    text_class_predictions = tuple(
        confidence_by_class.get(text_class) or 0.0
        for text_class in request_context.task_config.text_classes
    )
    return transferobject.SampleDTO.from_domain_object(sample, text_class_predictions)


@router.patch("/samples/{sample_id}")
def patch_sample(
    sample_id: str,
    sample_patch: types.SamplePatch,
    request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> transferobject.SampleDTO:
    """Patch (partial update) a sample."""
    with request_context.session_factory() as session:
        use_case = usecase.AnnotateSampleUseCase(session.sample_repository)
        sample = use_case(sample_id, sample_patch.text_class)
        session.commit()
    return transferobject.SampleDTO.from_domain_object(sample, ())
