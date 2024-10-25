"""Types and utilities for implementing the service/API."""

from typing import Optional

import pydantic

from nlpanno import domain


class BaseDTO(pydantic.BaseModel):
    """Base data transfer object."""

    model_config = pydantic.ConfigDict(frozen=True)


class SampleDTO(BaseDTO):
    """Data transfer object for a sample."""

    id: str
    text: str
    text_class: Optional[str] = pydantic.Field(serialization_alias="textClass")
    text_class_predictions: Optional[tuple[float, ...]] = pydantic.Field(
        serialization_alias="textClassPredictions"
    )

    @classmethod
    def from_domain_object(
        cls,
        domain_object: domain.Sample,
        text_class_predictions: tuple[float, ...],
    ) -> "SampleDTO":
        """Create a data transfer object from a domain object."""
        return cls(
            id=domain_object.id,
            text=domain_object.text,
            text_class=domain_object.text_class,
            text_class_predictions=text_class_predictions,
        )


class TaskConfigDTO(BaseDTO):
    """Data transfer object for a task config."""

    text_classes: tuple[str, ...] = pydantic.Field(serialization_alias="textClasses")

    @classmethod
    def from_domain_object(cls, domain_object: domain.AnnotationTask) -> "TaskConfigDTO":
        """Create a data transfer object from a domain object."""
        return cls(text_classes=domain_object.text_classes)
