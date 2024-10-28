import logging
import time
import nlpanno.container
from nlpanno import config

# TODO: use different logger.
_LOGGER = logging.getLogger("nlpanno")


def run() -> None:
    """Run the embedding worker."""
    settings = config.ApplicationSettings()
    container = nlpanno.container.create_container(settings)
    embed_all_samples_use_case = container.embed_all_samples_use_case()
    while True:
        did_work = embed_all_samples_use_case.execute()
        if not did_work:
            _LOGGER.info("No work to do, sleeping for 10 seconds.")
            time.sleep(10)


if __name__ == "__main__":
    run()
