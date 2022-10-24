import fastapi

from nlpanno import database, sampling, worker
from nlpanno.server import middlewares, routes, dependencies


def create_app(
    port: int,
    db: database.Database,
    sampler: sampling.Sampler = sampling.RandomSampler(),
):
    request_context_dependency = dependencies.create_request_context_dependency(
        db,
        sampler,
    )

    app = fastapi.FastAPI(
        dependencies=[request_context_dependency],
        on_startup=[
            lambda: worker.start_worker(port)
        ],
        on_shutdown=[worker.stop_worker],
    )


    middlewares.add_cors(app)

    app.include_router(routes.router)

    return app