"""Implementation of the fastAPI app."""

import fastapi

from nlpanno import sampling
from nlpanno.application import unitofwork
from nlpanno.domain import model

from . import controller_sample, controller_static, controller_task, middlewares, requestcontext


def create_app(
    unit_of_work_factory: unitofwork.UnitOfWorkFactory,
    task_config: model.AnnotationTask,
    sampler: sampling.Sampler,
    include_static_files: bool = True,
) -> fastapi.FastAPI:
    """Create the fastAPI app."""
    app = fastapi.FastAPI()

    requestcontext.setup_request_context(app, unit_of_work_factory, task_config, sampler)
    middlewares.add_middlewares(app)

    api_router = fastapi.APIRouter(prefix="/api")
    api_router.include_router(controller_sample.router)
    api_router.include_router(controller_task.router)
    app.include_router(api_router)

    if include_static_files:
        controller_static.initialize(app)

    return app
