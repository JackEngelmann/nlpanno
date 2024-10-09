"""Implementation of scripts."""

# pylint: disable=invalid-name, wrong-import-order

from typing import Optional

import uvicorn

import nlpanno.data
import nlpanno.sampling
import nlpanno.server
import nlpanno.worker

app = None


def start_server(
    database: nlpanno.data.Database,
    sampler: Optional[nlpanno.sampling.Sampler] = None,
    handle_update: Optional[nlpanno.worker.UpdateHandler] = None,
):
    """Start a server for annotation."""
    global app  # pylint: disable = global-statement

    if handle_update is None:
        handle_update = do_nothing
    if sampler is None:
        sampler = nlpanno.sampling.RandomSampler()

    app = nlpanno.server.create_app(database, sampler, handle_update)
    uvicorn.run("nlpanno.scripts:app")


def do_nothing():
    """No-op method (do nothing)."""
