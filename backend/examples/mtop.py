"""Example script to annotate MTOP data aided by mean embeddings."""

import nlpanno.data
import nlpanno.datasets
import nlpanno.scripts
import nlpanno.update

db = nlpanno.data.InMemoryDatabase()
mtop_dataset = nlpanno.datasets.MTOP(
	# The data for this example can be downloaded from https://fb.me/mtop_dataset.
	# You need to set the `data_path` to one of the subdirectories # (e.g. `.../de/` for German).
	"/Users/jackengelmann/Documents/Repositories/nlpanno/data/mtop/de",
	add_class_to_text=True,
	limit=1000,
)
mtop_dataset.fill_database(db)
handle_update = nlpanno.update.MeanEmbeddingUpdater(db, "distiluse-base-multilingual-cased-v1")

nlpanno.scripts.start_server(db, handle_update=handle_update)
