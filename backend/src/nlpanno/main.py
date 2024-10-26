"""Example script to annotate MTOP data aided by mean embeddings."""

import typer
import uvicorn

import nlpanno.logging
from nlpanno import config, container, datasets, domain
from nlpanno.adapters import annotation_api
from nlpanno.application import unitofwork

nlpanno.logging.configure_logging()

settings = config.ApplicationSettings()
dependency_container = container.DependencyContainer(settings)
server_app = None

app = typer.Typer()


@app.command()
def start_annotation() -> None:
    """Start the annotation server."""
    sampler = dependency_container.create_sampler()
    unit_of_work_factory = dependency_container.create_unit_of_work_factory()
    with unit_of_work_factory() as unit_of_work:
        unit_of_work.create_tables()
        task_config = _fill_db_with_test_data(unit_of_work)
        unit_of_work.commit()

    global server_app
    server_app = annotation_api.create_app(
        unit_of_work_factory,
        task_config,
        sampler,
        include_static_files=False,
    )
    uvicorn.run("nlpanno.main:server_app", log_config=None, port=settings.port, host=settings.host)


@app.command()
def start_embedding_loop() -> None:
    """Start the embedding loop."""
    embedding_processor = dependency_container.create_embedding_worker()
    embedding_processor.start()


@app.command()
def start_estimation_loop() -> None:
    """Start the estimation loop."""
    estimation_processor = dependency_container.create_estimation_worker()
    estimation_processor.start()


def _fill_db_with_test_data(unit_of_work: unitofwork.UnitOfWork) -> domain.AnnotationTask:
    mtop_dataset = datasets.MTOP(
        "/app/data",
        add_class_to_text=True,
        limit=100,
    )

    is_empty = len(unit_of_work.samples.find()) == 0
    if is_empty:
        for sample in mtop_dataset.samples:
            unit_of_work.samples.create(sample)

    return mtop_dataset.task_config
