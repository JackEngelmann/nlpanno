"""Implementation of tasks running in the background (e.g. model training)."""

import threading
from typing import Callable

UpdateHandler = Callable[[], None]


class Worker:
    """Worker triggering update when data changed."""

    def __init__(self, handle_update: UpdateHandler) -> None:
        self._new_data_event = threading.Event()

        self._thread = threading.Thread(
            target=_trigger_update_when_data_updated,
            args=[
                self._new_data_event,
                handle_update,
            ],
            daemon=True,
        )

    def start(self):
        """Start the worker."""
        self._thread.start()

    def end(self):
        """Cleanup when program is stopped."""
        # With the current implementation there is no cleanup necessary, because
        # the thread is a daemon (stops when main thread stops).
        # Cleanup might be necessary when implementation changes.

    def notify_data_update(self):
        """Method to notify the worker that data was updated."""
        # Set "new data" event to let the thread trigger the update handler.
        self._new_data_event.set()


def _trigger_update_when_data_updated(
    new_data_event: threading.Event, handle_update: UpdateHandler
):
    """Trigger the update handler when data was updated."""
    while True:
        # Wait until "new data" event is set.
        new_data_event.wait()

        # Immediately clear it since it is being handled.
        # When a change is made in the time handle_update runs, it will be
        # immediately run after handle_update is done.
        # When multiple changes happened in this time, only the last one will be
        # reacted to.
        new_data_event.clear()

        # Trigger the update handler.
        handle_update()
