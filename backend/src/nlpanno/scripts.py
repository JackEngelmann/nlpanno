from typing import Any, Callable, Optional
import uvicorn
import nlpanno.server
import nlpanno.database
import nlpanno.sampling
import uvicorn
import nlpanno.worker


app = None


def start_server(
    db: nlpanno.database.Database,
    sampler: Optional[nlpanno.sampling.Sampler] = None,
    handle_update: Optional[nlpanno.worker.UpdateHandler] = None,
 ):
    global app

    if handle_update is None:
        handle_update = lambda db: None
    if sampler is None:
        sampler = nlpanno.sampling.RandomSampler()

    app = nlpanno.server.create_app(db, sampler, handle_update)
    uvicorn.run("nlpanno.scripts:app")
