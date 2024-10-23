"""Implementation of dependencies common to all requests."""

import dataclasses

import fastapi

from nlpanno import data, sampling, worker, domain


@dataclasses.dataclass
class RequestContext:
	"""Request context."""

	database: data.SampleRepository
	task_config: domain.TaskConfig
	sampler: sampling.Sampler
	worker: worker.Worker


async def _get_request_context(request: fastapi.Request) -> data.SampleRepository:
	"""Get the request context from the app state."""
	return request.app.state.request_context


DEPENDS = fastapi.Depends(_get_request_context)
