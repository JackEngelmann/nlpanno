"""Implementation of fastAPI middlewares."""

import logging
import time
from typing import Callable

import asgi_correlation_id
import fastapi
import fastapi.middleware.cors

_LOGGER = logging.getLogger("nlpanno")


def add_middlewares(app: fastapi.FastAPI) -> None:
	"""Add middlewares to the app."""
	app.add_middleware(
		fastapi.middleware.cors.CORSMiddleware,
		allow_origins=["*"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)
	app.middleware("http")(log_request)
	app.add_middleware(asgi_correlation_id.CorrelationIdMiddleware)


async def log_request(request: fastapi.Request, call_next: Callable) -> fastapi.Response:
	"""Log the request and response."""
	_LOGGER.info(f"Received Request: {request.method} {request.url}")
	start_time = time.perf_counter()
	response = await call_next(request)
	process_time = time.perf_counter() - start_time
	_LOGGER.info(
		f"Sending Response: {response.status_code}; Process time: {process_time:.2f} seconds"
	)
	return response
