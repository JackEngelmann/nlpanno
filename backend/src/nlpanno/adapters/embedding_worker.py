import logging

import nlpanno.container
from nlpanno import config, worker
from nlpanno.application import usecase

# TODO: use different logger.
_LOGGER = logging.getLogger("nlpanno")


class EmbeddingWorker(worker.Worker):
    """Worker for embedding."""

    def __init__(
        self,
        embed_all_samples_use_case: usecase.EmbedAllSamplesUseCase,
    ) -> None:
        super().__init__(logger=_LOGGER, name="embedding", sleep_time=10)
        self._embed_all_samples_use_case = embed_all_samples_use_case

    def _process(self) -> worker.ProcessResult:
        """Process the worker."""
        did_work = self._embed_all_samples_use_case.execute()
        if not did_work:
            return worker.ProcessResult.NOTHING_TO_DO
        return worker.ProcessResult.FINISHED_WORK


def run() -> None:
    """Run the embedding worker."""
    settings = config.ApplicationSettings()
    container = nlpanno.container.create_container(settings)
    embed_all_samples_use_case = container.embed_all_samples_use_case()
    embedding_worker = EmbeddingWorker(embed_all_samples_use_case)
    embedding_worker.start()


if __name__ == "__main__":
    run()
