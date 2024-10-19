import dataclasses

from nlpanno import worker


@dataclasses.dataclass
class Status:
	"""Status of the server."""

	worker: worker.WorkerStatus
