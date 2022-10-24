import fastapi
from nlpanno import database, sampling


def create_request_context_dependency(db: database.Database, sampler: sampling.Sampler) -> fastapi.Depends:
    async def add_context_to_request(request: fastapi.Request):
        request.state.db = db
        request.state.sampler = sampler

    return fastapi.Depends(add_context_to_request)


async def _get_db_from_request_state(request: fastapi.Request) -> database.Database:
    return request.state.db


async def _get_sampler_from_request_state(request: fastapi.Request) -> sampling.Sampler:
    return request.state.sampler


SAMPLER = fastapi.Depends(_get_sampler_from_request_state)
DB = fastapi.Depends(_get_db_from_request_state)
