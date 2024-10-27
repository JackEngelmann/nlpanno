import dependency_injector.containers
import dependency_injector.providers
import sqlalchemy

import nlpanno.adapters.embedding_transformers
import nlpanno.adapters.persistence.sqlalchemy
import nlpanno.adapters.sampling
import nlpanno.application.unitofwork
import nlpanno.application.usecase
import nlpanno.config


class Container(dependency_injector.containers.DeclarativeContainer):
    config = dependency_injector.providers.Configuration()

    database_engine = dependency_injector.providers.Singleton(
        sqlalchemy.create_engine,
        config.database_url,
    )

    _sqlalchemy_session = dependency_injector.providers.Factory(
        sqlalchemy.orm.sessionmaker,
        bind=database_engine,
    )

    unit_of_work = dependency_injector.providers.Factory(
        nlpanno.adapters.persistence.sqlalchemy.SQLAlchemyUnitOfWork,
        database_engine,
    )

    ###
    # Services
    ###

    embedding_service = dependency_injector.providers.Factory(
        nlpanno.adapters.embedding_transformers.TransformersEmbeddingService,
        config.embedding_model_name,
    )

    embedding_aggregation_service = dependency_injector.providers.Factory(
        nlpanno.adapters.embedding_transformers.TransformersEmbeddingAggregationService,
    )

    sampling_service = dependency_injector.providers.Factory(
        nlpanno.adapters.sampling.RandomSamplingService,
    )

    vector_similarity_service = dependency_injector.providers.Factory(
        nlpanno.adapters.embedding_transformers.TransformersVectorSimilarityService,
    )

    ###
    # Use cases
    ###

    get_next_sample_use_case = dependency_injector.providers.Factory(
        nlpanno.application.usecase.GetNextSampleUseCase,
        sampling_service,
        unit_of_work,
    )

    annotate_sample_use_case = dependency_injector.providers.Factory(
        nlpanno.application.usecase.AnnotateSampleUseCase,
        unit_of_work,
    )

    embed_all_samples_use_case = dependency_injector.providers.Factory(
        nlpanno.application.usecase.EmbedAllSamplesUseCase,
        embedding_service,
        unit_of_work,
    )

    estimate_samples_use_case = dependency_injector.providers.Factory(
        nlpanno.application.usecase.EstimateSamplesUseCase,
        embedding_service,
        vector_similarity_service,
        unit_of_work,
    )

    fetch_annotation_task_use_case = dependency_injector.providers.Factory(
        nlpanno.application.usecase.FetchAnnotationTaskUseCase,
        unit_of_work,
    )


def create_container(settings: nlpanno.config.ApplicationSettings | None = None) -> Container:
    if settings is None:
        settings = nlpanno.config.ApplicationSettings()
    container = Container()
    container.config.from_dict(settings.model_dump())
    return container
