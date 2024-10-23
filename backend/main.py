"""Example script to annotate MTOP data aided by mean embeddings."""

import nlpanno.database
import nlpanno.datasets
import nlpanno.scripts
import nlpanno.update

mtop_dataset = nlpanno.datasets.MTOP(
	# The data for this example can be downloaded from https://fb.me/mtop_dataset.
	# You need to set the `data_path` to one of the subdirectories # (e.g. `.../de/` for German).
	"/Users/jackengelmann/Documents/Repositories/nlpanno/data/mtop/de",
	add_class_to_text=True,
	limit=1000,
)
sample_repository = nlpanno.database.SQLiteSampleRepository("mtop.db")
handle_update = nlpanno.update.MeanEmbeddingUpdater(sample_repository, "distiluse-base-multilingual-cased-v1", mtop_dataset.task_config)

nlpanno.scripts.start_server(sample_repository, mtop_dataset.task_config, handle_update=handle_update)