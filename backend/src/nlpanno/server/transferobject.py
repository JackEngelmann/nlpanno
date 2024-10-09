"""Types and utilities for implementing the service/API."""

# pylint: disable = too-few-public-methods
import functools
from typing import Any, Optional, Tuple

import pydantic

from nlpanno import data


class SampleDTO(pydantic.BaseModel, extra=pydantic.Extra.forbid):  # type: ignore
    """Data transfer object for a sample."""

    id: str
    text: str
    textClass: Optional[str]
    textClassPredictions: Optional[Tuple[float, ...]]

    @classmethod
    def from_domain_object(cls, domain_object: data.Sample):
        """Create the DTO from the domain object."""
        return cls(
            id=domain_object.id,
            text=domain_object.text,
            textClass=domain_object.text_class,
            textClassPredictions=domain_object.text_class_predictions,
        )


class TaskConfigDTO(pydantic.BaseModel, extra=pydantic.Extra.forbid):  # type: ignore
    """Data transfer object for a task config."""

    textClasses: Tuple[str, ...]

    @classmethod
    def from_domain_object(cls, domain_object: data.TaskConfig):
        """Create the DTO from the domain object."""
        return cls(textClasses=domain_object.text_classes)


@functools.singledispatch
def to_dto(domain_object: Any):
    """Transform domain objects to data transfer objects."""
    raise TypeError(
        f"type {type(domain_object)} it not supported by the 'to_dto' function."
    )


@to_dto.register
def _(domain_object: data.Sample):
    """Transform a sample."""
    return SampleDTO.from_domain_object(domain_object)


@to_dto.register
def _(domain_object: data.TaskConfig):
    """Transform a task config."""
    return TaskConfigDTO.from_domain_object(domain_object)


@to_dto.register
def _(domain_object: tuple):
    """Transform a tuple."""
    return list(to_dto(d) for d in domain_object)


@to_dto.register
def _(domain_object: list):
    """Transform a list."""
    return list(to_dto(d) for d in domain_object)
