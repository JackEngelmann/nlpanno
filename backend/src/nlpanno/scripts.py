"""Implementation of scripts."""

from typing import Optional

import uvicorn

import nlpanno.data
import nlpanno.sampling
import nlpanno.server
import nlpanno.worker

app = None


def start_server(
	database: nlpanno.data.Database,
	task_config: nlpanno.data.TaskConfig,
	sampler: Optional[nlpanno.sampling.Sampler] = None,
	handle_update: Optional[nlpanno.worker.UpdateHandler] = None,
	port: int = 8000,
) -> None:
	"""Start a server for annotation."""
	global app

	if handle_update is None:
		handle_update = do_nothing
	if sampler is None:
		sampler = nlpanno.sampling.RandomSampler()

	app = nlpanno.server.create_app(database, task_config, sampler, handle_update)
	uvicorn.run("nlpanno.scripts:app", log_config=None, port=port)


def do_nothing() -> None:
	"""No-op method (do nothing)."""
