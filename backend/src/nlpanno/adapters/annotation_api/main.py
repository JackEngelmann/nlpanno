import uvicorn

from nlpanno import config

from .app import create_app

app = create_app()


def run() -> None:
    application_settings = config.ApplicationSettings()
    uvicorn.run(
        "nlpanno.adapters.annotation_api.main:app",
        log_config=None,
        port=application_settings.port,
        host=application_settings.host,
    )


if __name__ == "__main__":
    run()
