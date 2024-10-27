"""Implementation of the fastAPI app."""

import fastapi

from nlpanno.application import service, unitofwork

from . import controller_sample, controller_static, controller_task, middlewares, requestcontext


def create_app(
    unit_of_work_factory: unitofwork.UnitOfWorkFactory,
    sampler: service.SamplingService,
    include_static_files: bool = True,
) -> fastapi.FastAPI:
    """Create the fastAPI app."""
    app = fastapi.FastAPI()

    requestcontext.setup_request_context(app, unit_of_work_factory, sampler)
    middlewares.add_middlewares(app)

    api_router = fastapi.APIRouter(prefix="/api")
    api_router.include_router(controller_sample.router)
    api_router.include_router(controller_task.router)
    app.include_router(api_router)

    if include_static_files:
        controller_static.initialize(app)

    return app
