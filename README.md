# nlpanno

nlpanno is an annotation tool for NLP tasks focused on annotation efficiency and extensibility.

**Annotation Efficiency.** Annotating data for text classification can be time-consuming, especially if there are many samples and text classes. Two ways to speed up the annotation are:
- **Speed up annotation of a sample.** The annotation tool can suggest the text class based on the information learned from previous annotations.
- **Annotate fewer samples.** Some samples are more valuable for model training than others (e.g., annotating a duplicate generally does not increase model performance). Estimating how valuable the annotation of a sample would be can help to produce a good model with fewer annotations.

**Extensibility.** For large annotation tasks, it makes sense to invest time in optimizing the annotation process for the concrete task or use case. Even with extensive configuration options, there often comes a point where you run into limitations. nlpanno is designed to be extendible. If none of the existing implementations fit, it should be easy to create your own.
Supported NLP Tasks. Currently, nlpanno focuses on the annotation for text classification tasks.

## Get started

The core concept of `nlpanno` is to implement a new server for each annotation task. 
The implementation should only take a few lines of code. A complete example is in `backend/examples/mtop`.

### Step 1: Define Database

First, you need a database implementation. Database implementations can be found in the `nlpanno.data` module. Example:
```python
db = nlpanno.data.InMemoryDatabase()
```
Alternatively, you can create your own implementation. The only requirement is that it implements the `nlpanno.data.Database` interface.

### Step 2: Fill the Database

Next, you need to fill the database with the information needed for the annotation task:
- A `TaskConfig`. This configuration contains metadata about the task (e.g., a list of available text classes).
- A list of `Sample`s that you want to annotate.

You can use your own data or use a pre-defined dataset from `nlpanno.datasets`. Example:
```python
dataset = nlpanno.datasets.MTOP("/path/to/data")
dataset.fill_database(db)
```

> [!NOTE]  
> The data for this example can be downloaded from https://fb.me/mtop_dataset. You need to set the `data_path` to one of the subdirectories (e.g. `.../de/` for German).

### Step 3: Setup Active Learning (Optional)

Next, you can specify an approach that predicts future labels. This is implemented as a callback (`handle_update`) that is triggered when the user annotate a sample.
Pre-defined implementations can be found in `nlpanno.update`. Example:
```python
handle_update = nlpanno.update.MeanEmbeddingUpdater(
    db, "distiluse-base-multilingual-cased-v1"
)
```

### Step 4: Start the Server

Finally, you can start the server (backend):
```python
nlpanno.scripts.start_server(db, handle_update=handle_update)
```

At the moment, the client applictation (frontend) needs to be started separately with `cd client && npm run start`.

You should see the annotation tool in the browser now on `http://localhost:3000/`.

## Disclaimer

`nlpanno` is a small hobby project and is currently not ready for productive use.
