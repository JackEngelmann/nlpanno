import abc
from nlpanno import database
import random
from typing import Tuple


class Sampler(abc.ABC):
    @abc.abstractmethod
    def __call__(self, samples: Tuple[database.Sample, ...]) -> database.Id:
        raise NotImplementedError()


class RandomSampler(Sampler):
    def __call__(self, samples: Tuple[database.Sample, ...]) -> database.Id:
        return random.sample(samples, 1)[0].id
