"""Implementation of the fastAPI app."""

import fastapi

from nlpanno import sampling, usecases
from nlpanno.annotation import api, middlewares, requestcontext, static
from nlpanno import domain
from nlpanno.database import inmemory


def create_app(
	sample_repository: usecases.SampleRepository,
	task_config: domain.AnnotationTask,
	sampler: sampling.Sampler,
	include_static_files: bool = True,
) -> fastapi.FastAPI:
	"""Create the fastAPI app."""
	app = fastapi.FastAPI()

	app.state.request_context = requestcontext.RequestContext(
		sample_repository,
		task_config,
		sampler,
	)
	middlewares.add_middlewares(app)
	app.include_router(api.router)

	if include_static_files:
		static.mount_static_files(app)
		app.include_router(static.router)

	return app
