"""Test suite for data module."""

import pytest
from nlpanno import database, domain


@staticmethod
def test_get_by_id(sample_repository: database.SampleRepository) -> None:
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
    sample_repository.create(sample_to_find)
    sample_repository.create(other_sample)
    found_sample = sample_repository.get_by_id(sample_to_find.id)
    assert found_sample is not None
    assert found_sample == sample_to_find


@staticmethod
def test_get_all(sample_repository: database.SampleRepository) -> None:
    """Test finding samples."""
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
    for sample in samples:
        sample_repository.create(sample)
    assert len(sample_repository.get_all()) == len(samples)

@staticmethod
def test_update(sample_repository: database.SampleRepository) -> None:
    """Test updating a sample."""
    sample_to_update = domain.Sample(
        domain.create_id(),
        "text 1",
        "class 1",
    )
    sample_repository.create(sample_to_update)
    updated_sample = domain.Sample(
        sample_to_update.id,
        "updated text",
        "class 2",
    )
    sample_repository.update(updated_sample)
    assert sample_repository.get_by_id(sample_to_update.id) == updated_sample

@staticmethod
def test_get_unlabeled(sample_repository: database.SampleRepository) -> None:
    """Test getting unlabeled samples."""
    unlabeled_id = domain.create_id()
    sample_repository.create(
        domain.Sample(domain.create_id(), "text 1", "class 1"),
    )
    sample_repository.create(
        domain.Sample(unlabeled_id, "text 2", None),
    )
    unlabeled_samples = sample_repository.get_unlabeled()
    assert len(unlabeled_samples) == 1
    assert unlabeled_samples[0].id == unlabeled_id


@pytest.fixture(params=("inmemory", "sqlite"))
def sample_repository(request: pytest.FixtureRequest) -> database.SampleRepository:
    """Sample repository fixture."""
    if request.param == "inmemory":
        return database.InMemorySampleRepository()
    if request.param == "sqlite":
        return database.SQLiteSampleRepository(":memory:")
    raise ValueError(f"Unknown sample repository: {request.param}")
