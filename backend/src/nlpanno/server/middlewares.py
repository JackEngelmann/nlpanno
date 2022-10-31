import fastapi
import fastapi.middleware.cors


def add_cors(app: fastapi.FastAPI):
    app.add_middleware(
        fastapi.middleware.cors.CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=['*'],
    )
