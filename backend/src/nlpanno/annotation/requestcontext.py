"""Implementation of dependencies common to all requests."""

import dataclasses

import fastapi

from nlpanno import domain, sampling
from nlpanno.application import unitofwork


@dataclasses.dataclass
class RequestContext:
    """Request context."""

    unit_of_work_factory: unitofwork.UnitOfWorkFactory
    task_config: domain.AnnotationTask
    sampler: sampling.Sampler


async def _get_request_context(request: fastapi.Request) -> RequestContext:
    """Get the request context from the app state."""
    request_context = request.app.state.request_context
    return request_context


DEPENDS = fastapi.Depends(_get_request_context)
