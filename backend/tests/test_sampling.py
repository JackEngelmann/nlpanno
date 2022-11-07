"""Test suit for sampling."""

from nlpanno import data, sampling


def test_random_sampler():
    """Test sampling with the random sampler."""
    random_sampler = sampling.RandomSampler()
    id_ = data.create_id()
    sample = data.Sample(
        id_,
        "text 1",
        None,
    )
    sampled_id = random_sampler((sample,))
    assert sampled_id == id_
