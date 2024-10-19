"""Module implementing sampling to pick the next sample to annotate."""

import abc
import random

from nlpanno import data


class Sampler(abc.ABC):
	"""Base class for all samplers."""

	@abc.abstractmethod
	def __call__(self, samples: tuple[data.Sample, ...]) -> data.Id:
		"""Pick a sample."""
		raise NotImplementedError()


class RandomSampler(Sampler):
	"""Sampler picking a random sample."""

	def __call__(self, samples: tuple[data.Sample, ...]) -> data.Id:
		"""Pick a random sample."""
		return random.sample(samples, 1)[0].id
