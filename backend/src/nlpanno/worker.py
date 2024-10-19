"""Implementation of tasks running in the background (e.g. model training)."""

import dataclasses
import threading
from typing import Callable

UpdateHandler = Callable[[], None]


@dataclasses.dataclass
class WorkerStatus:
	is_working: bool


class Worker:
	"""Worker triggering update when data changed."""

	def __init__(self, handle_update: UpdateHandler) -> None:
		self._new_data_event = threading.Event()
		self._is_working_event = threading.Event()

		self._thread = threading.Thread(
			target=self._run,
			args=(handle_update,),
			daemon=True,
		)

	def start(self) -> None:
		"""Start the worker."""
		self._thread.start()

	def end(self) -> None:
		"""Cleanup when program is stopped."""
		# With the current implementation there is no cleanup necessary, because
		# the thread is a daemon (stops when main thread stops).
		# Cleanup might be necessary when implementation changes.

	def notify_data_update(self) -> None:
		"""Method to notify the worker that data was updated."""
		# Set "new data" event to let the thread trigger the update handler.
		self._new_data_event.set()

	@property
	def is_working(self) -> bool:
		"""Check if the worker is currently executing the update handler."""
		return self._is_working_event.is_set()

	def _run(self, handle_update: UpdateHandler) -> None:
		"""Run the worker."""
		while True:
			# Wait until "new data" event is set.
			self._new_data_event.wait()

			# Immediately clear it since it is being handled.
			# When a change is made in the time handle_update runs, it will be
			# immediately run after handle_update is done.
			# When multiple changes happened in this time, only the last one will be
			# reacted to.
			self._new_data_event.clear()

			# Indicate that the worker is currently working.
			self._is_working_event.set()

			# Trigger the update handler.
			handle_update()

			# Indicate that the worker has finished its task.
			self._is_working_event.clear()

	def get_status(self) -> WorkerStatus:
		"""Get the status of the worker."""
		return WorkerStatus(is_working=self.is_working)
