import pathlib
from nlpanno import datasets, scripts, database

MTOP_PATH = pathlib.Path('/home/jack/Downloads/mtop/de')

ds_builder = datasets.MtopBuilder(MTOP_PATH, add_class_to_text=True)
db = database.InMemoryDatabase()
ds_builder.fill_database(db)
task_config = ds_builder.get_task_config()

scripts.start_server(db)
