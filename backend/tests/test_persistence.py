"""Test suite for data module."""

import pytest
import sqlalchemy.orm
import torch

import nlpanno.adapters.persistence.inmemory
import nlpanno.adapters.persistence.sqlalchemy
from nlpanno.application import unitofwork
from nlpanno.domain import model, repository

_ANNOTATION_TASK_ID = "task"
_TEXT_CLASS_1 = model.TextClass("c1", "class 1", _ANNOTATION_TASK_ID)
_TEXT_CLASS_2 = model.TextClass("c2", "class 2", _ANNOTATION_TASK_ID)


class TestSampleRepository:
    """Test suite for the sample repository."""

    @staticmethod
    def test_get_by_id(unit_of_work: unitofwork.UnitOfWork) -> None:
        """Test getting a sample by id."""
        sample_to_find = model.Sample(
            model.create_id(),
            _ANNOTATION_TASK_ID,
            "text 1",
            _TEXT_CLASS_1,
        )
        other_sample = model.Sample(
            model.create_id(),
            _ANNOTATION_TASK_ID,
            "text 2",
            _TEXT_CLASS_2,
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
        sample_to_update = model.Sample(
            model.create_id(),
            _ANNOTATION_TASK_ID,
            "text 1",
            _TEXT_CLASS_1,
        )
        with unit_of_work:
            unit_of_work.samples.create(sample_to_update)
            updated_sample = model.Sample(
                sample_to_update.id,
                _ANNOTATION_TASK_ID,
                "updated text",
                _TEXT_CLASS_2,
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
            (repository.SampleQuery(), ("1", "2", "3", "4")),
            (repository.SampleQuery(has_label=True), ("1", "4")),
            (repository.SampleQuery(has_label=False), ("2", "3")),
            (repository.SampleQuery(has_embedding=True), ("3", "4")),
            (repository.SampleQuery(has_embedding=False), ("1", "2")),
            (repository.SampleQuery(task_id="task 1"), ("1", "2")),
        ],
    )
    def test_find(
        unit_of_work: unitofwork.UnitOfWork,
        query: repository.SampleQuery,
        expected_sample_ids: tuple[model.Id, ...],
    ) -> None:
        """Test finding samples by query."""
        samples = (
            model.Sample("1", "task 1", "text 1", _TEXT_CLASS_1),
            model.Sample("2", "task 1", "text 2", None),
            model.Sample("3", "task 2", "text 3", None, torch.rand(10)),
            model.Sample("4", "task 2", "text 4", _TEXT_CLASS_2, torch.rand(10)),
        )
        with unit_of_work:
            for sample in samples:
                unit_of_work.samples.create(sample)
            unit_of_work.commit()
            found_samples = unit_of_work.samples.find(query)
        assert len(found_samples) == len(expected_sample_ids)
        found_sample_ids = tuple(sample.id for sample in found_samples)
        assert set(found_sample_ids) == set(expected_sample_ids)


class TestAnnotationTaskRepository:
    """Test suite for the annotation task repository."""

    @staticmethod
    def test_get_by_id(unit_of_work: unitofwork.UnitOfWork) -> None:
        """Test getting an annotation task by id."""
        task_to_find = model.AnnotationTask(model.create_id(), ())
        task_to_find.create_text_class("class 1")
        other_task = model.AnnotationTask(model.create_id(), ())
        with unit_of_work:
            unit_of_work.annotation_tasks.create(task_to_find)
            unit_of_work.annotation_tasks.create(other_task)
            unit_of_work.commit()
            found_task = unit_of_work.annotation_tasks.get_by_id(task_to_find.id)
            assert found_task is not None
            assert found_task == task_to_find


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
