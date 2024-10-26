import json
import logging
from types import TracebackType
from typing import Optional, Self

import sqlalchemy
import torch
from sqlalchemy import orm

from nlpanno.application import unitofwork
from nlpanno.domain import model, repository

_LOG = logging.getLogger("nlpanno")


class Base(sqlalchemy.orm.DeclarativeBase):
    """Base class for all SQLAlchemy models."""


class Sample(Base):
    """Model for a sample."""

    __tablename__ = "samples"

    id: orm.Mapped[str] = orm.mapped_column(primary_key=True)
    text: orm.Mapped[str]
    text_class: orm.Mapped[Optional[str]]
    embedding: orm.Mapped[Optional[str]]
    estimates: orm.Mapped[list["ClassEstimate"]] = orm.relationship()

    def to_domain(self) -> model.Sample:
        embedding = None if self.embedding is None else torch.tensor(json.loads(self.embedding))
        return model.Sample(
            id=self.id,
            text=self.text,
            text_class=self.text_class,
            embedding=embedding,
            estimates=tuple(estimate.to_domain() for estimate in self.estimates),
        )

    @classmethod
    def from_domain(cls, sample: model.Sample) -> Self:
        embedding = None if sample.embedding is None else json.dumps(sample.embedding.tolist())
        return cls(
            id=sample.id,
            text=sample.text,
            text_class=sample.text_class,
            embedding=embedding,
            estimates=list(ClassEstimate.from_domain(estimate) for estimate in sample.estimates),
        )


class ClassEstimate(Base):
    """Model for an estimate."""

    __tablename__ = "estimates"

    id: orm.Mapped[str] = orm.mapped_column(primary_key=True)
    text_class: orm.Mapped[str]
    confidence: orm.Mapped[float]
    sample_id: orm.Mapped[str] = orm.mapped_column(sqlalchemy.ForeignKey("samples.id"))

    def to_domain(self) -> model.ClassEstimate:
        return model.ClassEstimate(
            id=self.id,
            text_class=self.text_class,
            confidence=self.confidence,
        )

    @classmethod
    def from_domain(cls, estimate: model.ClassEstimate) -> Self:
        return cls(
            id=estimate.id,
            text_class=estimate.text_class,
            confidence=estimate.confidence,
        )


class SQLAlchemySampleRepository(repository.SampleRepository):
    """Sample repository using SQLAlchemy."""

    def __init__(self, session: orm.Session) -> None:
        self._session = session

    def get_by_id(self, sample_id: model.Id) -> model.Sample:
        persistence_sample = self._session.get(Sample, sample_id)
        if persistence_sample is None:
            raise ValueError(f"Sample with id {sample_id} not found")
        return persistence_sample.to_domain()

    def get_all(self) -> tuple[model.Sample, ...]:
        persistence_samples = self._session.query(Sample).all()
        return tuple(persistence_sample.to_domain() for persistence_sample in persistence_samples)

    def update(self, sample: model.Sample) -> None:
        persistence_sample = Sample.from_domain(sample)
        self._session.merge(persistence_sample)

    def create(self, sample: model.Sample) -> None:
        persistence_sample = Sample.from_domain(sample)
        self._session.add(persistence_sample)

    def find(self, query: repository.SampleQuery | None = None) -> tuple[model.Sample, ...]:
        select_statement = sqlalchemy.select(Sample)
        select_statement = self._apply_filters(select_statement, query)
        persistence_samples = self._session.scalars(select_statement).all()
        return tuple(persistence_sample.to_domain() for persistence_sample in persistence_samples)

    def _apply_filters(
        self, statement: sqlalchemy.sql.Select, query: repository.SampleQuery | None
    ) -> sqlalchemy.sql.Select:
        if query is None:
            return statement
        statement = self._apply_filter_has_label(statement, query)
        statement = self._apply_filter_has_embedding(statement, query)
        return statement

    def _apply_filter_has_label(
        self, statement: sqlalchemy.sql.Select, query: repository.SampleQuery
    ) -> sqlalchemy.sql.Select:
        if query.has_label is True:
            return statement.where(Sample.text_class.is_not(None))
        elif query.has_label is False:
            return statement.where(Sample.text_class.is_(None))
        return statement

    def _apply_filter_has_embedding(
        self, statement: sqlalchemy.sql.Select, query: repository.SampleQuery
    ) -> sqlalchemy.sql.Select:
        if query.has_embedding is True:
            return statement.where(Sample.embedding.is_not(None))
        elif query.has_embedding is False:
            return statement.where(Sample.embedding.is_(None))
        return statement


class SQLAlchemyUnitOfWork(unitofwork.UnitOfWork):
    """Database session using SQLAlchemy."""

    def __init__(self, engine: sqlalchemy.engine.Engine) -> None:
        self._engine = engine

    def __enter__(self) -> Self:
        self._session = sqlalchemy.orm.Session(self._engine)
        return self

    def __exit__(
        self,
        exc_type: type[Exception] | None,
        exc_value: Exception | None,
        traceback: TracebackType | None,
    ) -> None:
        # Can always rollback, because it does no harm.
        # If an error occurs, the rollback will be done here.
        # If the session is committed, the rollback does not change anything.
        self._session.rollback()
        self._session.close()

    @property
    def samples(self) -> SQLAlchemySampleRepository:
        return SQLAlchemySampleRepository(self._session)

    def commit(self) -> None:
        _LOG.info("Committing session")
        self._session.commit()

    def create_tables(self) -> None:
        _LOG.info("Creating tables")
        Base.metadata.create_all(self._engine)


class SQLAlchemyUnitOfWorkFactory(unitofwork.UnitOfWorkFactory):
    """Session factory using SQLAlchemy."""

    def __init__(self, engine: sqlalchemy.engine.Engine) -> None:
        self._engine = engine

    def __call__(self) -> unitofwork.UnitOfWork:
        return SQLAlchemyUnitOfWork(self._engine)
