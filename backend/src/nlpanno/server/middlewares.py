"""Implementation of fastAPI middlewares."""

import fastapi
import fastapi.middleware.cors


def add_cors(app: fastapi.FastAPI):
    """Add cors middleware with very loose rules."""
    app.add_middleware(
        fastapi.middleware.cors.CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
