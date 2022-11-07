"""Module implementing sampling to pick the next sample to annotate."""

# pylint: disable = too-few-public-methods
import abc
import random
from typing import Tuple

from nlpanno import data


class Sampler(abc.ABC):
    """Base class for all samplers."""

    @abc.abstractmethod
    def __call__(self, samples: Tuple[data.Sample, ...]) -> data.Id:
        """Pick a sample."""
        raise NotImplementedError()


class RandomSampler(Sampler):
    """Sampler picking a random sample."""

    def __call__(self, samples: Tuple[data.Sample, ...]) -> data.Id:
        """Pick a random sample."""
        return random.sample(samples, 1)[0].id
