# nlpanno

`nlpanno` is an annotation tool for NLP tasks. It aims to assist the annotation and is designed to be extendable.

**Disclaimer**: this is a tiny hobby project and not meant for productive use.

**Supported NLP Tasks.** Currently, `nlpanno` focuses on the annotation for _text classification_ tasks.

**Assist the Annotation.** Annotating data for text classification can be time-consuming. Especially, if there is a large number of available text classes and a large number of samples. Two ways to speed up the annotation are:
- Make it quicker to annotate a sample. This can be done by using the information from previous annotations to improve the future annotations. Given a sample, a model can rank the classes by its prediction on how likely this annotation is.
- Annotate fewer samples. It might not be necessary to annotate the full set. A model can be used to order the annotations by estimating how helpful they would be for training a model.

**Extendability.** For large annotation tasks, it makes sense to invest time in optimizing the annotation process for the concrete task / use case. Even with extensive configuration options, there often comes a point where you run into limitations. `nlpanno` is designed to be extendible. If none of the existing implementations fit, the aim is to make it easy to create your own.

## Get started

The main idea is to create a new server for each annotation task. Therefore, a small script is implemented that defines & runs the server. A full example is in `backend/examples/mtop`.

### Step 1: Define Database

First, you need a database implementation. Database implementation can be found in the `nlpanno.data` module. Example:
```python
db = nlpanno.data.InMemoryDatabase()
```
Alternatively, you can create your own implementation. The only requirement is that it implements the `nlpanno.data.Database` interface.

### Step 2: Fill the Database

Next, you need to fill the database with information. Specifically, it needs:
- A `TaskConfig`. This configures the annotation task. It contains a list of all available text classes.
- A list of `Sample`s. These are the samples that you want to annotate.

`nlpanno.datasets` contains pre-defined datasets that can be used to fill the database. Example:
```python
data_path = pathlib.Path("path/to/data")
builder = nlpanno.datasets.MtopBuilder(data_path)
builder.build(db)
```
The data for this example can be downloaded from https://fb.me/mtop_dataset. You need to set the `data_path` to one of the subdirectories (e.g. `.../de/` for German).

You can also define your own way to fill the database.

### Step 3: Setup Active Learning

An active learning approach uses the information from the annotations you already did to help you with the annotations you still have to do.

In `nlpanno`, this is implemented as a callback (`handle_update`) that is triggered when the user annotate a sample.
Implementations can be found in `nlpanno.update`. Example:
```python
handle_update = nlpanno.update.MeanEmbeddingUpdater(
    db, "distiluse-base-multilingual-cased-v1"
)
```

### Step 4: Start the Server

Now that everything is defined, you can start the server (backend):
```python
nlpanno.scripts.start_server(db, handle_update=handle_update)
```

At the moment, the frontend needs to be started separately with `cd client && npm run start`.

Now, you should see the annotation tool in the browser on `http://localhost:3000/`.
