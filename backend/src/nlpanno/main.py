"""Example script to annotate MTOP data aided by mean embeddings."""

import logging
from collections.abc import Sequence

import pydantic_settings
import sentence_transformers
import torch
import typer
import uvicorn

import nlpanno.annotation
import nlpanno.database
import nlpanno.datasets
import nlpanno.embedding
import nlpanno.estimation
import nlpanno.sampling
from nlpanno import domain

_LOGGER = logging.getLogger(__name__)


class Settings(pydantic_settings.BaseSettings):
	"""Settings for the application."""

	# model_config = pydantic_settings.SettingsConfigDict(env_file=".env")

	samples_database_path: str = "samples.db"
	embeddings_database_path: str = "embeddings.db"
	estimations_database_path: str = "estimations.db"
	embedding_model_name: str = "distiluse-base-multilingual-cased-v1"
	port: int = 8000
	# TODO: Add dataset options.


app = typer.Typer()


@app.command()
def start_embedding_loop() -> None:
	"""Start the embedding loop."""
	logging.basicConfig(level=logging.INFO)
	settings = Settings()
	sample_repository = nlpanno.database.SQLiteSampleRepository(settings.samples_database_path)
	model = sentence_transformers.SentenceTransformer(settings.embedding_model_name)

	def embedding_function(samples: Sequence[domain.Sample]) -> Sequence[domain.Embedding]:
		texts = list(sample.text for sample in samples)
		return model.encode(texts, convert_to_tensor=True)  # type: ignore

	embedding_processor = nlpanno.embedding.EmbeddingProcessor(
		embedding_function, sample_repository
	)
	embedding_processor.loop()


@app.command()
def start_estimation_loop() -> None:
	"""Start the estimation loop."""
	logging.basicConfig(level=logging.INFO)
	settings = Settings()
	sample_repository = nlpanno.database.SQLiteSampleRepository(settings.samples_database_path)

	def embedding_aggregation_function(embeddings: Sequence[domain.Embedding]) -> domain.Embedding:
		stacked = torch.stack(list(embeddings), dim=0)
		return torch.mean(stacked, dim=0)

	def vector_similarity_function(
		sample_embedding: domain.Embedding, class_embedding: domain.Embedding
	) -> float:
		return sentence_transformers.util.pytorch_cos_sim(class_embedding, sample_embedding).item()

	estimation_processor = nlpanno.estimation.EstimationProcessor(
		sample_repository,
		embedding_aggregation_function,
		vector_similarity_function,
	)
	estimation_processor.loop()


server_app = None


@app.command()
def start_annotation() -> None:
	"""Start the annotation server."""
	settings = Settings()
	mtop_dataset = nlpanno.datasets.MTOP(
		# The data for this example can be downloaded from https://fb.me/mtop_dataset.
		# You need to set the `data_path` to one of the subdirectories
		# (e.g. `.../de/` for German).
		"/Users/jackengelmann/Documents/Repositories/nlpanno/data/mtop/de",
		add_class_to_text=True,
		limit=1000,
	)
	sample_repository = nlpanno.database.SQLiteSampleRepository(settings.samples_database_path)
	with sample_repository as sample_repository:
		for sample in mtop_dataset.samples:
			sample_repository.create(sample)
	global server_app
	server_app = nlpanno.annotation.create_app(
		sample_repository,
		mtop_dataset.task_config,
		nlpanno.sampling.RandomSampler(),
	)
	uvicorn.run("nlpanno.main:server_app", log_config=None, port=settings.port)
