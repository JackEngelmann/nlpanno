"""Test suit for the update worker."""
# pylint: disable=wrong-import-order,import-error,duplicate-code

import time

import pytest_mock

import nlpanno.worker


def test_worker_no_update(mocker: pytest_mock.MockFixture):
    """Test not triggering udpate."""
    update = mocker.MagicMock()
    worker = nlpanno.worker.Worker(update)
    worker.start()
    time.sleep(0.1)
    worker.end()
    update.assert_not_called()


def test_worker_one_update(mocker: pytest_mock.MockFixture):
    """Test trigering update once."""
    update = mocker.MagicMock()
    worker = nlpanno.worker.Worker(update)
    worker.start()
    worker.notify_data_update()
    time.sleep(0.1)
    worker.end()
    update.assert_called_once()


def test_worker_two_updates(mocker: pytest_mock.MockFixture):
    """Test triggering update twice."""
    update = mocker.MagicMock()
    worker = nlpanno.worker.Worker(update)
    worker.start()
    worker.notify_data_update()
    time.sleep(0.1)
    worker.notify_data_update()
    time.sleep(0.1)
    worker.end()
    assert update.call_count == 2


def test_worker_skip_in_between(mocker: pytest_mock.MockFixture):
    """Test that only the latest update is triggered."""

    def long_update():
        time.sleep(0.2)

    update = mocker.MagicMock(wraps=long_update)
    worker = nlpanno.worker.Worker(update)
    worker.start()
    # Work on the first one.
    worker.notify_data_update()
    # Skip the one in between.
    worker.notify_data_update()
    time.sleep(0.1)
    # Work on the last one.
    worker.notify_data_update()
    worker.end()
    time.sleep(0.3)
    assert update.call_count == 2
