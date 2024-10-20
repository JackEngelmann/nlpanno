"""Test suit for the update worker."""

import time

import pytest_mock

import nlpanno.worker


def test_worker_no_update(mocker: pytest_mock.MockFixture) -> None:
	"""Test not triggering udpate."""
	update = mocker.MagicMock()
	worker = nlpanno.worker.Worker(update)
	worker.start()
	time.sleep(0.1)
	worker.end()
	update.assert_not_called()


def test_worker_one_update(mocker: pytest_mock.MockFixture) -> None:
	"""Test trigering update once."""
	update = mocker.MagicMock()
	worker = nlpanno.worker.Worker(update)
	worker.start()
	worker.notify_data_update()
	time.sleep(0.1)
	worker.end()
	update.assert_called_once()


def test_worker_two_updates(mocker: pytest_mock.MockFixture) -> None:
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


def test_worker_skip_in_between(mocker: pytest_mock.MockFixture) -> None:
	"""Test that only the latest update is triggered."""

	def long_update() -> None:
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


def test_is_working(mocker: pytest_mock.MockFixture) -> None:
	"""Test the is_working property."""

	def long_update() -> None:
		time.sleep(0.2)

	update = mocker.MagicMock(wraps=long_update)
	worker = nlpanno.worker.Worker(update)
	worker.start()
	assert not worker.is_working

	# Start working.
	worker.notify_data_update()

	# Is working.
	time.sleep(0.1)
	assert worker.is_working

	# Is finished.
	time.sleep(0.2)
	assert not worker.is_working
