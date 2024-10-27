import random
from collections.abc import Sequence

from nlpanno.application import service
from nlpanno.domain import model


class RandomSamplingService(service.SamplingService):
    def sample(self, samples: Sequence[model.Sample]) -> model.Id | None:
        if len(samples) == 0:
            return None
        id_ = random.sample(samples, 1)[0].id
        return id_
