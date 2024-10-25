"""Test suite for data module."""

import pytest
import sqlalchemy.orm

from nlpanno import database, domain, infrastructure


class TestSampleRepository:
	"""Test suite for the sample repository."""

	@staticmethod
	def test_get_by_id(session_factory: infrastructure.SessionFactory) -> None:
		"""Test getting a sample by id."""
		sample_to_find = domain.Sample(
			domain.create_id(),
			"text 1",
			"class 1",
		)
		other_sample = domain.Sample(
			domain.create_id(),
			"text 2",
			"class 2",
		)
		with session_factory() as session:
			sample_repository = session.sample_repository
			sample_repository.create(sample_to_find)
			sample_repository.create(other_sample)
			session.commit()
			found_sample = sample_repository.get_by_id(sample_to_find.id)
			assert found_sample is not None
			assert found_sample == sample_to_find

	@staticmethod
	def test_get_all(session_factory: infrastructure.SessionFactory) -> None:
		"""Test getting all samples."""
		samples = (
			domain.Sample(
				domain.create_id(),
				"text 1",
				"class 1",
			),
			domain.Sample(
				domain.create_id(),
				"text 2",
				"class 1",
			),
			domain.Sample(
				domain.create_id(),
				"text 3",
				"class 2",
			),
		)
		with session_factory() as session:
			sample_repository = session.sample_repository
			for sample in samples:
				sample_repository.create(sample)
			session.commit()
			assert len(sample_repository.get_all()) == len(samples)

	@staticmethod
	def test_update(session_factory: infrastructure.SessionFactory) -> None:
		"""Test updating a sample."""
		sample_to_update = domain.Sample(
			domain.create_id(),
			"text 1",
			"class 1",
		)
		with session_factory() as session:
			sample_repository = session.sample_repository
			sample_repository.create(sample_to_update)
			updated_sample = domain.Sample(
				sample_to_update.id,
				"updated text",
				"class 2",
			)
			sample_repository.update(updated_sample)
			session.commit()
			assert sample_repository.get_by_id(sample_to_update.id) == updated_sample

	@staticmethod
	def test_get_unlabeled(session_factory: infrastructure.SessionFactory) -> None:
		"""Test getting unlabeled samples."""
		unlabeled_id = domain.create_id()
		with session_factory() as session:
			sample_repository = session.sample_repository
			sample_repository.create(domain.Sample(domain.create_id(), "text 1", "class 1"))
			sample_repository.create(domain.Sample(unlabeled_id, "text 2", None))
			session.commit()
			unlabeled_samples = sample_repository.get_unlabeled()
			assert len(unlabeled_samples) == 1
			assert unlabeled_samples[0].id == unlabeled_id


@pytest.fixture(params=("inmemory", "sqlalchemy"))
def session_factory(request: pytest.FixtureRequest) -> infrastructure.SessionFactory:
	"""Session factory fixture."""
	if request.param == "inmemory":
		return database.InMemorySessionFactory()
	if request.param == "sqlalchemy":
		engine = sqlalchemy.create_engine("sqlite://")
		session_factory = database.SQLAlchemySessionFactory(engine)
		with session_factory() as session:
			session.create_tables()
			session.commit()
		return session_factory
	raise ValueError(f"Unknown session factory: {request.param}")
