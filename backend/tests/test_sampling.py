"""Test suit for sampling."""

from nlpanno import sampling, domain


def test_random_sampler() -> None:
	"""Test sampling with the random sampler."""
	random_sampler = sampling.RandomSampler()
	id_ = domain.create_id()
	sample = domain.Sample(
		id_,
		"text 1",
		None,
	)
	sampled_id = random_sampler((sample,))
	assert sampled_id == id_
