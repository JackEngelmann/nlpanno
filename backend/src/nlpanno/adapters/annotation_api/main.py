import uvicorn

from nlpanno import config


def run() -> None:
    application_settings = config.ApplicationSettings()
    uvicorn.run(
        "nlpanno.adapters.annotation_api.app:app",
        log_config=None,
        port=application_settings.port,
        host=application_settings.host,
    )


if __name__ == "__main__":
    run()
