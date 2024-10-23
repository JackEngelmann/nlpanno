"""Implementation of the fastAPI app."""

import fastapi
import fastapi.templating

import nlpanno.server.logging
import nlpanno.worker
from nlpanno import database, domain, sampling
from nlpanno.server import api, middlewares, requestcontext, static


def create_app(
	sample_repository: database.SampleRepository,
	task_config: domain.TaskConfig,
	sampler: sampling.Sampler,
	handle_update: nlpanno.worker.UpdateHandler,
) -> fastapi.FastAPI:
	"""Create the fastAPI app."""
	nlpanno.server.logging.configure_logging()

	app = fastapi.FastAPI()

	worker = nlpanno.worker.Worker(handle_update)
	app.add_event_handler("startup", worker.start)
	app.add_event_handler("shutdown", worker.end)
	request_context = requestcontext.RequestContext(
		sample_repository,
		task_config,
		sampler,
		worker,
	)
	app.state.request_context = request_context

	middlewares.add_middlewares(app)
	static.mount_static_files(app)
	app.include_router(api.router)
	app.include_router(static.router)

	return app
