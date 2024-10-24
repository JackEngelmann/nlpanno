from nlpanno import domain, usecases
import json
import torch
import sqlalchemy
from sqlalchemy import orm
from typing import Optional, Self

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

    def to_domain(self) -> domain.Sample:
        embedding = None if self.embedding is None else torch.tensor(json.loads(self.embedding))
        return domain.Sample(
            id=self.id,
            text=self.text,
            text_class=self.text_class,
            embedding=embedding,
            estimates=tuple(estimate.to_domain() for estimate in self.estimates),
        )

    @classmethod
    def from_domain(cls, sample: domain.Sample) -> Self:
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

	def to_domain(self) -> domain.ClassEstimate:
		return domain.ClassEstimate(
			id=self.id,
			text_class=self.text_class,
			confidence=self.confidence,
		)

	@classmethod
	def from_domain(cls, estimate: domain.ClassEstimate) -> Self:
		return cls(
			id=estimate.id,
			text_class=estimate.text_class,
			confidence=estimate.confidence,
		)


class SQLAlchemySampleRepository(usecases.SampleRepository):
    """Sample repository using SQLAlchemy."""

    def __init__(self, engine: sqlalchemy.Engine) -> None:
        self._engine = engine
    
    def __enter__(self) -> Self:
        self._session = sqlalchemy.orm.Session(self._engine)
        Base.metadata.create_all(self._engine)
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._session.close()

    def add(self, sample: domain.Sample) -> None:
        persistence_sample = Sample.from_domain(sample)
        self._session.add(persistence_sample)

    def get_by_id(self, sample_id: domain.Id) -> domain.Sample:
        persistence_sample = self._session.get(Sample, sample_id)
        if persistence_sample is None:
            raise ValueError(f"Sample with id {sample_id} not found")
        return persistence_sample.to_domain()

    def get_all(self) -> tuple[domain.Sample, ...]:
        persistence_samples = self._session.query(Sample).all()
        return tuple(persistence_sample.to_domain() for persistence_sample in persistence_samples)

    def update(self, sample: domain.Sample) -> None:
        persistence_sample = Sample.from_domain(sample)
        self._session.merge(persistence_sample)

    def get_unlabeled(self) -> tuple[domain.Sample, ...]:
        persistence_samples = self._session.query(Sample).filter(Sample.text_class == None).all()
        return tuple(persistence_sample.to_domain() for persistence_sample in persistence_samples)

    def get_labeled(self) -> tuple[domain.Sample, ...]:
        persistence_samples = self._session.query(Sample).filter(Sample.text_class != None).all()
        return tuple(persistence_sample.to_domain() for persistence_sample in persistence_samples)

    def get_unembedded(self) -> tuple[domain.Sample, ...]:
        persistence_samples = self._session.query(Sample).filter(Sample.embedding == None).all()
        return tuple(persistence_sample.to_domain() for persistence_sample in persistence_samples)

    def create(self, sample: domain.Sample) -> None:
        persistence_sample = Sample.from_domain(sample)
        self._session.add(persistence_sample)
