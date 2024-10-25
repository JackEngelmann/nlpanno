"""Implementation of the fastAPI app."""

import fastapi

from nlpanno import domain, infrastructure, sampling
from nlpanno.annotation import api, middlewares, requestcontext, static


def create_app(
	session_factory: infrastructure.SessionFactory,
	task_config: domain.AnnotationTask,
	sampler: sampling.Sampler,
	include_static_files: bool = True,
) -> fastapi.FastAPI:
	"""Create the fastAPI app."""
	app = fastapi.FastAPI()

	app.state.request_context = requestcontext.RequestContext(
		session_factory,
		task_config,
		sampler,
	)
	middlewares.add_middlewares(app)
	app.include_router(api.router)

	if include_static_files:
		static.mount_static_files(app)
		app.include_router(static.router)

	return app
