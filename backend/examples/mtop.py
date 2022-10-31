import pathlib
from statistics import mean
from nlpanno import datasets, scripts, database
from nlpanno.update import meanembedding

MTOP_PATH = pathlib.Path('/home/jack/Downloads/mtop/de')

db = database.InMemoryDatabase()
datasets.MtopBuilder(MTOP_PATH, add_class_to_text=True).build(db)
mean_embedding_updater = meanembedding.MeanEmbeddingUpdater(db, "distiluse-base-multilingual-cased-v1")

scripts.start_server(db, handle_update=mean_embedding_updater.handle_update)
