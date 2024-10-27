import pydantic_settings


class ApplicationSettings(pydantic_settings.BaseSettings):
    """Settings for the application."""

    # TODO: Use env file.
    model_config = pydantic_settings.SettingsConfigDict(env_prefix="NLPANNO_")

    database_url: str = "sqlite:///samples.db"
    embedding_model_name: str = "distiluse-base-multilingual-cased-v1"
    port: int = 8000
    host: str = "0.0.0.0"
    # TODO: Add dataset options.

    backend_serves_static_files: bool = False
