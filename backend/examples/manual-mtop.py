import pathlib
from nlpanno import datasets, scripts, database

MTOP_PATH = pathlib.Path('/home/jack/Downloads/mtop/de')

db = database.InMemoryDatabase()
ds_builder = datasets.MtopBuilder(MTOP_PATH, add_class_to_text=True)
ds_builder.build(db)

scripts.start_server(db)
