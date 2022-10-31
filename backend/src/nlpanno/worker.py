import threading
from turtle import update
from typing import Callable


UpdateHandler = Callable[[], None]


class Worker:
    def __init__(self, handle_update: UpdateHandler) -> None:
        self._new_data_event = threading.Event()

        self._thread = threading.Thread(
            target=trigger_update_when_data_changed,
            args=[
                self._new_data_event,
                handle_update,
            ],
            daemon=True,
        )

    def start(self):
        self._thread.start()
    
    def end(self):
        # With the current implementation there is no cleanup necessary, because
        # the thread is a daemon (stops when main thread stops).
        # Cleanup might be necessary when implementation changes.
        pass

    def notify_data_update(self):
        # Set "new data" event to let the thread trigger the update handler.
        self._new_data_event.set()


def trigger_update_when_data_changed(new_data_event: threading.Event, handle_update: UpdateHandler):
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

