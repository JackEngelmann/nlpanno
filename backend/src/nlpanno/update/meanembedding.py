from nlpanno import database
from typing import Dict, Optional, Tuple
import torch
import sentence_transformers
import sentence_transformers.util
import collections
import copy


class MeanEmbeddingUpdater:
    def __init__(self, db: database.Database, model_name: str) -> None:
        self._db = db
        self._embedding_by_id: Optional[Dict[str, torch.tensor]] = None
        self._model = sentence_transformers.SentenceTransformer(model_name)
        self._initialized = True
    
    def handle_update(self):
        print('start update', flush=True)
        task_config = self._db.get_task_config()
        samples = self._db.find_samples()

        if self._embedding_by_id is None:
            self._fill_embedding_by_id(samples)

        group_embeddings = self._calc_group_embeddings(samples)
        for sample in samples:
            # TODO: don't predict classes that already have ground truth?
            text_class_predictions = self._calc_text_class_predictions(
                group_embeddings,
                self._embedding_by_id[sample.id],
                task_config
            )

            # TODO: introduce partial update? avoid copy
            sample = self._db.get_sample_by_id(sample.id)  # could have changed
            sample_copy = copy.deepcopy(sample)
            sample_copy.text_class_predictions = text_class_predictions
            self._db.update_sample(sample_copy)
        print('start update', flush=True)

    def _calc_text_class_predictions(
        self,
        group_embeddings: Dict[str, torch.tensor],
        sample_embedding: torch.tensor,
        task_config: database.TaskConfig
    ) -> Tuple[float, ...]:
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

    
    def _calc_group_embeddings(self, samples) -> Dict[str, torch.tensor]:
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
    
    def _fill_embedding_by_id(self, samples: Tuple[database.Sample, ...]):
        texts = tuple(s.text for s in samples)
        embeddings = tuple(self._model.encode(texts, convert_to_tensor=True))
        self._embedding_by_id = {}
        for sample, embedding in zip(samples, embeddings):
            self._embedding_by_id[sample.id] = embedding