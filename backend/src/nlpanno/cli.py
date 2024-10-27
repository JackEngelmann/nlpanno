"""Example script to annotate MTOP data aided by mean embeddings."""

import typer

import nlpanno.adapters.annotation_api.main
import nlpanno.adapters.embedding_worker
import nlpanno.adapters.estimation_worker
import nlpanno.logging

# TODO: think about how to configure logging in a better way
nlpanno.logging.configure_logging()

app = typer.Typer()


@app.command()
def start_annotation_server() -> None:
    """Start the annotation server."""
    nlpanno.adapters.annotation_api.main.run()


@app.command()
def start_embedding_worker() -> None:
    """Start the embedding worker."""
    nlpanno.adapters.embedding_worker.run()


@app.command()
def start_estimation_worker() -> None:
    """Start the estimation worker."""
    nlpanno.adapters.estimation_worker.run()


if __name__ == "__main__":
    app()
