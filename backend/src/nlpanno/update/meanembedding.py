"""Active learning using mean embeddings."""

# pylint: disable=too-few-public-methods

import collections
import copy
from typing import Dict, Optional, Tuple

import sentence_transformers
import sentence_transformers.util
import torch

from nlpanno import data


class MeanEmbeddingUpdater:
    """Updater using mean embeddings to predict potential text classes."""

    def __init__(self, database: data.Database, model_name: str) -> None:
        self._database = database
        self._embedding_by_id: Optional[Dict[str, torch.Tensor]] = None
        self._model = sentence_transformers.SentenceTransformer(model_name)
        self._initialized = True

    def __call__(self):
        """Make new predictions when the data was updated."""
        print("start update", flush=True)
        task_config = self._database.get_task_config()
        samples = self._database.find_samples()

        if self._embedding_by_id is None:
            self._fill_embedding_by_id(samples)

        group_embeddings = self._calc_group_embeddings(samples)
        for sample in samples:
            # pylint: disable = fixme
            # TODO: don't predict classes that already have ground truth?
            text_class_predictions = self._predict_text_classes(
                group_embeddings, self._embedding_by_id[sample.id], task_config
            )

            # pylint: disable = fixme
            # TODO: introduce partial update? avoid copy
            sample = self._database.get_sample_by_id(sample.id)  # could have changed
            sample_copy = copy.deepcopy(sample)
            sample_copy.text_class_predictions = text_class_predictions
            self._database.update_sample(sample_copy)
        print("end update", flush=True)

    def _predict_text_classes(
        self,
        group_embeddings: Dict[str, torch.Tensor],
        sample_embedding: torch.Tensor,
        task_config: data.TaskConfig,
    ) -> Tuple[float, ...]:
        """Predict text classes for one sample."""
        similarities = []
        for group in task_config.text_classes:
            if group not in group_embeddings:
                similarity = 0.0
            else:
                similarity = sentence_transformers.util.pytorch_cos_sim(
                    group_embeddings[group],
                    sample_embedding,
                ).item()
            similarities.append(similarity)
        return tuple(similarities)

    def _calc_group_embeddings(self, samples) -> Dict[str, torch.Tensor]:
        """Calculate all group embeddings (avg embedding of samples of the group)."""
        assert self._embedding_by_id is not None
        embeddings_by_group = collections.defaultdict(list)
        for sample in samples:
            group = sample.text_class
            if group is not None:
                embedding = self._embedding_by_id[sample.id]
                embeddings_by_group[group].append(embedding)
        group_embeddings = {
            group: torch.mean(torch.stack(embeddings, dim=0), dim=0)
            for group, embeddings in embeddings_by_group.items()
        }
        return group_embeddings

    def _fill_embedding_by_id(self, samples: Tuple[data.Sample, ...]):
        """Write all sample embeddings into the cache."""
        texts = list(s.text for s in samples)
        embeddings = tuple(self._model.encode(texts, convert_to_tensor=True))
        self._embedding_by_id = {}
        for sample, embedding in zip(samples, embeddings):
            self._embedding_by_id[sample.id] = embedding
