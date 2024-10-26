"""Implementation of the fastAPI app."""

import fastapi

from nlpanno import domain, sampling
from nlpanno.application import usecase, unitofwork
from nlpanno.annotation import api, middlewares, requestcontext, static


def create_app(
    unit_of_work_factory: unitofwork.UnitOfWorkFactory,
    task_config: domain.AnnotationTask,
    sampler: sampling.Sampler,
    include_static_files: bool = True,
) -> fastapi.FastAPI:
    """Create the fastAPI app."""
    app = fastapi.FastAPI()

    app.state.request_context = requestcontext.RequestContext(
        unit_of_work_factory,
        task_config,
        sampler,
    )
    middlewares.add_middlewares(app)
    app.include_router(api.router)

    if include_static_files:
        static.mount_static_files(app)
        app.include_router(static.router)

    return app
