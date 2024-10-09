"""Example script to annotate MTOP data aided by mean embeddings."""

import pathlib

import nlpanno.data
import nlpanno.datasets
import nlpanno.scripts
import nlpanno.update

# 1. Define DB.
db = nlpanno.data.InMemoryDatabase()

# 2. Fill DB.
# The data for this example can be downloaded from https://fb.me/mtop_dataset.
# You need to set the `data_path` to one of the subdirectories
# (e.g. `.../de/` for German).
mtop_data_path = pathlib.Path(
    "/Users/jackengelmann/Documents/Repositories/nlpanno/data/mtop/de"
)
nlpanno.datasets.MtopBuilder(mtop_data_path, add_class_to_text=True).build(db)

# 3. Setup active learning.
# The MeanEmbeddingUpdater calculates a single embedding for each text class by
# calculating the mean of all the samples that are currently annotated as this class.
# Class predictions are made by comparing the embedding of a sample to the class
# embeddings and calculating the similarity. The class predictions are saved in the
# database.
handle_update = nlpanno.update.MeanEmbeddingUpdater(
    db, "distiluse-base-multilingual-cased-v1"
)

# 4. Start server (backend).
nlpanno.scripts.start_server(db, handle_update=handle_update)

# The frontend must be started separately: cd client && npm run start.
# It could also be started in this script, but for development it is more
# convenient if it runs separetely (e.g. enable hot-reloading).
