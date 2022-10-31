import functools
from typing import Any, Callable
import fastapi

import nlpanno.worker
from nlpanno import database, sampling
from nlpanno.server import middlewares, requestcontext, routes


def create_app(
    db: database.Database,
    sampler: sampling.Sampler,
    handle_update: nlpanno.worker.UpdateHandler,
):
    worker = nlpanno.worker.Worker(handle_update)
    request_context = requestcontext.RequestContext(
        db,
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