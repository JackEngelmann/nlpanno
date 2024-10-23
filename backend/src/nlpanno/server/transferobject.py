"""Types and utilities for implementing the service/API."""

from typing import Any, Optional

import pydantic

from nlpanno import domain, worker
from nlpanno.server import status


class BaseDTO(pydantic.BaseModel):
	"""Base data transfer object."""

	model_config = pydantic.ConfigDict(frozen=True)

	@classmethod
	def from_domain_object(cls, domain_object: Any) -> "BaseDTO":  # noqa: ANN401
		"""Create a data transfer object from a domain object."""
		raise NotImplementedError("Subclasses must implement this method.")


class WorkerStatusDTO(BaseDTO):
	"""Data transfer object for the status of the worker."""

	is_working: bool = pydantic.Field(serialization_alias="isWorking")

	@classmethod
	def from_domain_object(cls, domain_object: worker.WorkerStatus) -> "WorkerStatusDTO":
		"""Create a data transfer object from a domain object."""
		return cls(is_working=domain_object.is_working)


class StatusDTO(BaseDTO):
	"""Data transfer object for the status of the server."""

	worker: WorkerStatusDTO = pydantic.Field(serialization_alias="worker")

	@classmethod
	def from_domain_object(cls, domain_object: status.Status) -> "StatusDTO":
		"""Create a data transfer object from a domain object."""
		return cls(worker=WorkerStatusDTO.from_domain_object(domain_object.worker))


class SampleDTO(BaseDTO):
	"""Data transfer object for a sample."""

	id: str
	text: str
	text_class: Optional[str] = pydantic.Field(serialization_alias="textClass")
	text_class_predictions: Optional[tuple[float, ...]] = pydantic.Field(
		serialization_alias="textClassPredictions"
	)

	@classmethod
	def from_domain_object(cls, domain_object: domain.Sample) -> "SampleDTO":
		"""Create a data transfer object from a domain object."""
		return cls(
			id=domain_object.id,
			text=domain_object.text,
			text_class=domain_object.text_class,
			text_class_predictions=domain_object.text_class_predictions,
		)


class TaskConfigDTO(BaseDTO):
	"""Data transfer object for a task config."""

	text_classes: tuple[str, ...] = pydantic.Field(serialization_alias="textClasses")

	@classmethod
	def from_domain_object(cls, domain_object: domain.TaskConfig) -> "TaskConfigDTO":
		"""Create a data transfer object from a domain object."""
		return cls(text_classes=domain_object.text_classes)
