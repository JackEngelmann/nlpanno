"""Implementation of the fastAPI app."""

import fastapi

import nlpanno.worker
from nlpanno import data, sampling
from nlpanno.server import middlewares, requestcontext, routes


def create_app(
    database: data.Database,
    sampler: sampling.Sampler,
    handle_update: nlpanno.worker.UpdateHandler,
) -> fastapi.FastAPI:
    """Create the fastAPI app."""
    worker = nlpanno.worker.Worker(handle_update)
    request_context = requestcontext.RequestContext(
        database,
        sampler,
        worker,
    )

    app = fastapi.FastAPI()
    app.state.request_context = request_context

    app.add_event_handler("startup", worker.start)
    app.add_event_handler("shutdown", worker.end)

    middlewares.add_cors(app)

    app.include_router(routes.router)

    return app
