"""Active learning using mean embeddings."""

import collections
import logging
from typing import Callable, Optional

import sentence_transformers
import sentence_transformers.util
import torch

from nlpanno import data

_LOGGER = logging.getLogger("nlpanno")

_EmbeddingFunction = Callable[[list[str]], list[torch.Tensor]]


class EmbeddingCache:
	"""Cache for embeddings."""

	def __init__(self, embedding_function: _EmbeddingFunction) -> None:
		self._embedding_function = embedding_function
		self._embedding_by_id: dict[str, torch.Tensor] = {}

	def prefill(self, samples: tuple[data.Sample, ...]) -> None:
		"""Prefill the cache with embeddings for a list of samples."""
		self._load_missing_embeddings(samples)

	def get_embedding(self, sample: data.Sample) -> torch.Tensor:
		"""Get the embedding for a sample."""
		embedding = self._embedding_by_id.get(sample.id)
		if embedding is None:
			_LOGGER.debug(f"Cache miss for sample {sample.id}")
			embedding, *_ = self._embedding_function([sample.text])
			self._embedding_by_id[sample.id] = embedding
		return embedding

	def _load_missing_embeddings(self, samples: tuple[data.Sample, ...]) -> None:
		"""Load missing embeddings for a list of samples."""
		samples_to_embed = [sample for sample in samples if sample.id not in self._embedding_by_id]
		if len(samples_to_embed) == 0:
			return

		_LOGGER.debug(f"Embedding {len(samples_to_embed)} samples")
		texts = [sample.text for sample in samples_to_embed]
		embeddings = self._embedding_function(texts)
		for sample, embedding in zip(samples_to_embed, embeddings):
			self._embedding_by_id[sample.id] = embedding


class MeanEmbeddingUpdater:
	"""Updater using mean embeddings to predict potential text classes."""

	def __init__(self, database: data.Database, model_name: str) -> None:
		self._database = database
		model = sentence_transformers.SentenceTransformer(model_name)

		def embedding_function(texts: list[str]) -> list[torch.Tensor]:
			return model.encode(texts, convert_to_tensor=True)  # type: ignore

		self._embedding_cache = EmbeddingCache(embedding_function)

	def __call__(self) -> None:
		"""Make new predictions when the data was updated."""
		samples = self._database.find_samples()
		self._embedding_cache.prefill(samples)
		task_config = self._database.get_task_config()
		class_embeddings = self._derive_class_embeddings(samples)
		for sample in samples:
			if sample.text_class is not None:
				continue
			sample_embedding = self._embedding_cache.get_embedding(sample)
			text_class_predictions = self._predict(sample_embedding, class_embeddings, task_config)
			sample = self._database.get_sample_by_id(sample.id)  # could have changed
			sample.text_class_predictions = text_class_predictions
			self._database.update_sample(sample)

	def _predict(
		self,
		sample_embedding: torch.Tensor,
		class_embeddings: dict[str, torch.Tensor],
		task_config: data.TaskConfig,
	) -> tuple[float, ...]:
		"""Predict text classes for one sample."""
		return tuple(
			_derive_vector_similarity(sample_embedding, class_embeddings.get(text_class))
			for text_class in task_config.text_classes
		)

	def _derive_class_embeddings(self, samples: tuple[data.Sample, ...]) -> dict[str, torch.Tensor]:
		"""Calculate all class embeddings (avg embedding of samples of the class)."""
		_LOGGER.info("Starting to derive class embeddings")
		embeddings_by_class: dict[str, list[torch.Tensor]] = collections.defaultdict(list)
		for sample in samples:
			if sample.text_class is None:
				continue
			embedding = self._embedding_cache.get_embedding(sample)
			embeddings_by_class[sample.text_class].append(embedding)
		class_embeddings = {
			text_class: torch.mean(torch.stack(embeddings, dim=0), dim=0)
			for text_class, embeddings in embeddings_by_class.items()
		}
		_LOGGER.info("Finished deriving class embeddings")
		return class_embeddings


def _derive_vector_similarity(
	sample_embedding: torch.Tensor,
	class_embedding: Optional[torch.Tensor],
) -> float:
	"""Calculate the vector similarity between two embeddings."""
	if class_embedding is None:
		return 0.0
	return sentence_transformers.util.pytorch_cos_sim(class_embedding, sample_embedding).item()
