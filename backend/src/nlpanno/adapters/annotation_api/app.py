"""Implementation of the fastAPI app."""

import fastapi

import nlpanno.container
from nlpanno import datasets
from nlpanno.application import unitofwork

from . import controller_sample, controller_static, controller_task, middlewares


def create_app(include_static_files: bool = True) -> fastapi.FastAPI:
    """Create the fastAPI app."""
    settings = nlpanno.config.ApplicationSettings()
    container = nlpanno.container.create_container(settings)

    unit_of_work = container.unit_of_work()
    _setup_db(unit_of_work)

    app = fastapi.FastAPI()
    middlewares.add_middlewares(app)

    api_router = fastapi.APIRouter(prefix="/api")
    api_router.include_router(controller_sample.router)
    api_router.include_router(controller_task.router)
    app.include_router(api_router)
    if include_static_files:
        controller_static.initialize(app)

    return app


app = create_app()


def _setup_db(unit_of_work: unitofwork.UnitOfWork) -> None:
    with unit_of_work:
        unit_of_work.create_tables()
        _fill_db_with_test_data(unit_of_work)
        unit_of_work.commit()


# TODO: remove this or at least make it prettier.
def _fill_db_with_test_data(unit_of_work: unitofwork.UnitOfWork) -> None:
    mtop_dataset = datasets.MTOP(
        "/app/data",
        add_class_to_text=True,
        limit=100,
    )

    is_empty = len(unit_of_work.samples.find()) == 0
    if is_empty:
        for sample in mtop_dataset.samples:
            unit_of_work.samples.create(sample)
        unit_of_work.annotation_tasks.create(mtop_dataset.task_config)
