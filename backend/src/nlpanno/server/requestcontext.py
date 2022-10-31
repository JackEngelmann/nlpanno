import fastapi
from nlpanno import database, sampling, worker
import dataclasses


@dataclasses.dataclass
class RequestContext:
    db: database.Database
    sampler: sampling.Sampler
    worker: worker.Worker


async def _get_request_context(request: fastapi.Request) -> database.Database:
    return request.app.state.request_context


DEPENDS = fastapi.Depends(_get_request_context)
