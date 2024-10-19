"""Types and utilities for implementing the service/API."""

import functools
from typing import Any, Optional

import pydantic

from nlpanno import data, worker


class StatusDTO(pydantic.BaseModel):
	"""Data transfer object for the status of the server."""

	is_working: bool = pydantic.Field(serialization_alias="isWorking")


class SampleDTO(pydantic.BaseModel, extra=pydantic.Extra.forbid):  # type: ignore
	"""Data transfer object for a sample."""

	id: str
	text: str
	text_class: Optional[str] = pydantic.Field(serialization_alias="textClass")
	text_class_predictions: Optional[tuple[float, ...]] = pydantic.Field(
		serialization_alias="textClassPredictions"
	)


class TaskConfigDTO(pydantic.BaseModel, extra=pydantic.Extra.forbid):  # type: ignore
	"""Data transfer object for a task config."""

	text_classes: tuple[str, ...] = pydantic.Field(serialization_alias="textClasses")


@functools.singledispatch
def to_dto(domain_object: Any) -> Any:  # noqa: ANN401
	"""Transform domain objects to data transfer objects."""
	raise TypeError(f"type {type(domain_object)} it not supported by the 'to_dto' function.")


@to_dto.register
def _(domain_object: data.Sample) -> SampleDTO:
	"""Transform a sample."""
	return SampleDTO(
		id=domain_object.id,
		text=domain_object.text,
		text_class=domain_object.text_class,
		text_class_predictions=domain_object.text_class_predictions,
	)


@to_dto.register
def _(domain_object: data.TaskConfig) -> TaskConfigDTO:
	"""Transform a task config."""
	return TaskConfigDTO(text_classes=domain_object.text_classes)


@to_dto.register
def _(domain_object: worker.WorkerStatus) -> StatusDTO:
	"""Transform a worker status."""
	return StatusDTO(is_working=domain_object.is_working)


@to_dto.register
def _(domain_object: tuple) -> list:
	"""Transform a tuple."""
	return list(to_dto(d) for d in domain_object)


@to_dto.register
def _(domain_object: list) -> list:
	"""Transform a list."""
	return list(to_dto(d) for d in domain_object)
