"""Test suit for sampling."""

from nlpanno.adapters import sampling
from nlpanno.domain import model


def test_random_sampling_service() -> None:
    """Test sampling with the random sampler."""
    random_sampler = sampling.RandomSamplingService()
    id_ = model.create_id()
    sample = model.Sample(
        id_,
        "task_id",
        "text 1",
        None,
    )
    sampled_id = random_sampler.sample((sample,))
    assert sampled_id == id_
