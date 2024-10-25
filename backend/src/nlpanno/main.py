"""Example script to annotate MTOP data aided by mean embeddings."""

import logging
from collections.abc import Sequence
from typing import Callable

import typer
import uvicorn

from nlpanno import config, domain, container, annotation, datasets, infrastructure


settings = config.ApplicationSettings()
dependency_container = container.DependencyContainer(settings)
server_app = None

app = typer.Typer()


@app.command()
def start_annotation() -> None:
	"""Start the annotation server."""
	logging.basicConfig(level=logging.DEBUG)
	sampler = dependency_container.create_sampler()
	session_factory = dependency_container.create_session_factory()
	with session_factory() as session:
		session.create_tables()
		task_config = _fill_db_with_test_data(session)
		session.commit()

	global server_app
	server_app = annotation.create_app(
		session_factory,
		task_config,
		sampler,
		include_static_files=False,
	)
	uvicorn.run("nlpanno.main:server_app", log_config=None, port=settings.port, host=settings.host)


@app.command()
def start_embedding_loop() -> None:
	"""Start the embedding loop."""
	logging.basicConfig(level=logging.INFO)
	embedding_processor = dependency_container.create_embedding_processor()
	embedding_processor.loop()


@app.command()
def start_estimation_loop() -> None:
	"""Start the estimation loop."""
	logging.basicConfig(level=logging.INFO)
	estimation_processor = dependency_container.create_estimation_processor()
	estimation_processor.loop()


def _fill_db_with_test_data(session: infrastructure.Session) -> domain.AnnotationTask:
	# Skip if the database is already filled.
	if len(session.sample_repository.get_all()) == 0:
		return

	mtop_dataset = datasets.MTOP(
		"/app/data",
		add_class_to_text=True,
		limit=100,
	)
	if len(session.sample_repository.get_all()) == 0:
		for sample in mtop_dataset.samples:
			session.sample_repository.create(sample)
	return mtop_dataset.task_config