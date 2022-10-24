from nlpanno import sampling, database


def test_random_sampler():
    random_sampler = sampling.RandomSampler()
    id_ = database.create_id()
    sample = database.Sample(
        id_,
        'text 1',
        None,
    )
    sampled_id = random_sampler((sample,))
    assert sampled_id == id_
