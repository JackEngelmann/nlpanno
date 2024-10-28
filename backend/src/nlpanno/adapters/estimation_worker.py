import logging

import nlpanno.container
from nlpanno import config

# TODO: use different logger.
_LOGGER = logging.getLogger("nlpanno")


def run() -> None:
    """Run the estimation worker."""
    settings = config.ApplicationSettings()
    container = nlpanno.container.create_container(settings)
    estimate_samples_use_case = container.estimate_samples_use_case()
    while True:
        estimate_samples_use_case.execute()


if __name__ == "__main__":
    run()
