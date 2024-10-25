"""Implementation of dependencies common to all requests."""

import dataclasses

import fastapi

from nlpanno import domain, infrastructure, sampling


@dataclasses.dataclass
class RequestContext:
	"""Request context."""

	session_factory: infrastructure.SessionFactory
	task_config: domain.AnnotationTask
	sampler: sampling.Sampler


async def _get_request_context(request: fastapi.Request) -> RequestContext:
	"""Get the request context from the app state."""
	request_context = request.app.state.request_context
	return request_context


DEPENDS = fastapi.Depends(_get_request_context)
