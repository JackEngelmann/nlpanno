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


class TextClass(Base):
    """Model for a text class."""

    __tablename__ = "text_classes"

    id: orm.Mapped[str] = orm.mapped_column(primary_key=True)
    name: orm.Mapped[str]
    annotation_task_id: orm.Mapped[str] = orm.mapped_column(
        sqlalchemy.ForeignKey("annotation_tasks.id")
    )

    def to_domain(self) -> model.TextClass:
        return model.TextClass(
            id=self.id, name=self.name, annotation_task_id=self.annotation_task_id
        )

    @classmethod
    def from_domain(cls, text_class: model.TextClass) -> Self:
        return cls(
            id=text_class.id,
            name=text_class.name,
            annotation_task_id=text_class.annotation_task_id,
        )


class AnnotationTask(Base):
    """Model for an annotation task."""

    __tablename__ = "annotation_tasks"

    id: orm.Mapped[str] = orm.mapped_column(primary_key=True)
    text_classes: orm.Mapped[list[TextClass]] = orm.relationship()
    name: orm.Mapped[str]

    def to_domain(self) -> model.AnnotationTask:
        return model.AnnotationTask(
            id=self.id,
            name=self.name,
            text_classes=tuple(text_class.to_domain() for text_class in self.text_classes),
        )

    @classmethod
    def from_domain(cls, task: model.AnnotationTask) -> Self:
        text_classes = list(TextClass.from_domain(text_class) for text_class in task.text_classes)
        return cls(id=task.id, name=task.name, text_classes=text_classes)


class Sample(Base):
    """Model for a sample."""

    __tablename__ = "samples"

    id: orm.Mapped[str] = orm.mapped_column(primary_key=True)
    text: orm.Mapped[str]
    text_class_id: orm.Mapped[Optional[str]] = orm.mapped_column(
        sqlalchemy.ForeignKey("text_classes.id")
    )
    text_class: orm.Mapped[Optional[TextClass]] = orm.relationship()
    embedding: orm.Mapped[Optional[str]]
    estimates: orm.Mapped[list["ClassEstimate"]] = orm.relationship()
    annotation_task_id: orm.Mapped[str] = orm.mapped_column(
        sqlalchemy.ForeignKey("annotation_tasks.id")
    )

    def to_domain(self) -> model.Sample:
        embedding = None if self.embedding is None else torch.tensor(json.loads(self.embedding))
        text_class = None if self.text_class is None else self.text_class.to_domain()
        return model.Sample(
            id=self.id,
            text=self.text,
            text_class=text_class,
            embedding=embedding,
            estimates=tuple(estimate.to_domain() for estimate in self.estimates),
            annotation_task_id=self.annotation_task_id,
        )

    @classmethod
    def from_domain(cls, sample: model.Sample) -> Self:
        embedding = None if sample.embedding is None else json.dumps(sample.embedding.tolist())
        text_class = None if sample.text_class is None else TextClass.from_domain(sample.text_class)
        return cls(
            id=sample.id,
            text=sample.text,
            text_class=text_class,
            embedding=embedding,
            estimates=list(ClassEstimate.from_domain(estimate) for estimate in sample.estimates),
            annotation_task_id=sample.annotation_task_id,
        )


class ClassEstimate(Base):
    """Model for an estimate."""

    __tablename__ = "estimates"

    id: orm.Mapped[str] = orm.mapped_column(primary_key=True)
    text_class_id: orm.Mapped[str] = orm.mapped_column(sqlalchemy.ForeignKey("text_classes.id"))
    confidence: orm.Mapped[float]
    sample_id: orm.Mapped[str] = orm.mapped_column(sqlalchemy.ForeignKey("samples.id"))

    def to_domain(self) -> model.ClassEstimate:
        return model.ClassEstimate(
            id=self.id,
            text_class_id=self.text_class_id,
            confidence=self.confidence,
        )

    @classmethod
    def from_domain(cls, estimate: model.ClassEstimate) -> Self:
        return cls(
            id=estimate.id,
            text_class_id=estimate.text_class_id,
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
        statement = self._apply_filter_task_id(statement, query)
        return statement

    def _apply_filter_has_label(
        self, statement: sqlalchemy.sql.Select, query: repository.SampleQuery
    ) -> sqlalchemy.sql.Select:
        if query.has_label is True:
            return statement.where(Sample.text_class_id.is_not(None))
        elif query.has_label is False:
            return statement.where(Sample.text_class_id.is_(None))
        return statement

    def _apply_filter_has_embedding(
        self, statement: sqlalchemy.sql.Select, query: repository.SampleQuery
    ) -> sqlalchemy.sql.Select:
        if query.has_embedding is True:
            return statement.where(Sample.embedding.is_not(None))
        elif query.has_embedding is False:
            return statement.where(Sample.embedding.is_(None))
        return statement

    def _apply_filter_task_id(
        self, statement: sqlalchemy.sql.Select, query: repository.SampleQuery
    ) -> sqlalchemy.sql.Select:
        if query.task_id is not None:
            return statement.where(Sample.annotation_task_id == query.task_id)
        return statement


class SQLAlchemyAnnotationTaskRepository(repository.AnnotationTaskRepository):
    """Annotation task repository using SQLAlchemy."""

    def __init__(self, session: orm.Session) -> None:
        self._session = session

    def get_by_id(self, task_id: model.Id) -> model.AnnotationTask:
        persistence_task = self._session.get(AnnotationTask, task_id)
        if persistence_task is None:
            raise ValueError(f"Annotation task with id {task_id} not found")
        return persistence_task.to_domain()

    def update(self, task: model.AnnotationTask) -> None:
        persistence_task = AnnotationTask.from_domain(task)
        self._session.merge(persistence_task)

    def create(self, task: model.AnnotationTask) -> None:
        persistence_task = AnnotationTask.from_domain(task)
        self._session.add(persistence_task)

    def find(self) -> tuple[model.AnnotationTask, ...]:
        persistence_tasks = self._session.query(AnnotationTask).all()
        return tuple(persistence_task.to_domain() for persistence_task in persistence_tasks)


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
    def annotation_tasks(self) -> SQLAlchemyAnnotationTaskRepository:
        return SQLAlchemyAnnotationTaskRepository(self._session)

    @property
    def samples(self) -> SQLAlchemySampleRepository:
        return SQLAlchemySampleRepository(self._session)

    def commit(self) -> None:
        _LOG.info("Committing session")
        self._session.commit()

    def create_tables(self) -> None:
        _LOG.info("Creating tables")
        Base.metadata.create_all(self._engine)
