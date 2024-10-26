"""Test suite for data module."""

import pytest
import sqlalchemy.orm
import torch

import nlpanno.adapters.persistence.inmemory
import nlpanno.adapters.persistence.sqlalchemy
from nlpanno import domain
from nlpanno.application import unitofwork


class TestSampleRepository:
    """Test suite for the sample repository."""

    @staticmethod
    def test_get_by_id(unit_of_work: unitofwork.UnitOfWork) -> None:
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
        with unit_of_work:
            unit_of_work.samples.create(sample_to_find)
            unit_of_work.samples.create(other_sample)
            unit_of_work.commit()
            found_sample = unit_of_work.samples.get_by_id(sample_to_find.id)
            assert found_sample is not None
            assert found_sample == sample_to_find

    @staticmethod
    def test_update(unit_of_work: unitofwork.UnitOfWork) -> None:
        """Test updating a sample."""
        sample_to_update = domain.Sample(
            domain.create_id(),
            "text 1",
            "class 1",
        )
        with unit_of_work:
            unit_of_work.samples.create(sample_to_update)
            updated_sample = domain.Sample(
                sample_to_update.id,
                "updated text",
                "class 2",
            )
            unit_of_work.samples.update(updated_sample)
            unit_of_work.commit()
            found_sample = unit_of_work.samples.get_by_id(sample_to_update.id)
            assert found_sample is not None
            assert found_sample == updated_sample

    @staticmethod
    @pytest.mark.parametrize(
        "query, expected_sample_ids",
        [
            (domain.SampleQuery(), ("1", "2", "3", "4")),
            (domain.SampleQuery(has_label=True), ("1", "4")),
            (domain.SampleQuery(has_label=False), ("2", "3")),
            (domain.SampleQuery(has_embedding=True), ("3", "4")),
            (domain.SampleQuery(has_embedding=False), ("1", "2")),
        ],
    )
    def test_find(
        unit_of_work: unitofwork.UnitOfWork,
        query: domain.SampleQuery,
        expected_sample_ids: tuple[domain.Id, ...],
    ) -> None:
        """Test finding samples by query."""
        samples = (
            domain.Sample("1", "text 1", "class"),
            domain.Sample("2", "text 2", None),
            domain.Sample("3", "text 3", None, torch.rand(10)),
            domain.Sample("4", "text 4", "class", torch.rand(10)),
        )
        with unit_of_work:
            for sample in samples:
                unit_of_work.samples.create(sample)
            unit_of_work.commit()
            found_samples = unit_of_work.samples.find(query)
        assert len(found_samples) == len(expected_sample_ids)
        found_sample_ids = tuple(sample.id for sample in found_samples)
        assert set(found_sample_ids) == set(expected_sample_ids)


@pytest.fixture(params=("inmemory", "sqlalchemy"))
def unit_of_work(request: pytest.FixtureRequest) -> unitofwork.UnitOfWork:
    """Fixture creating a unit of work."""
    factory: unitofwork.UnitOfWorkFactory
    if request.param == "inmemory":
        factory = nlpanno.adapters.persistence.inmemory.InMemoryUnitOfWorkFactory()
    elif request.param == "sqlalchemy":
        engine = sqlalchemy.create_engine("sqlite://")
        factory = nlpanno.adapters.persistence.sqlalchemy.SQLAlchemyUnitOfWorkFactory(engine)
    else:
        raise ValueError(f"Unknown unit of work factory: {request.param}")
    unit_of_work = factory()
    with unit_of_work:
        unit_of_work.create_tables()
        unit_of_work.commit()
    return unit_of_work
