"""Schemas for the API."""

from typing import Optional

import pydantic

from nlpanno import domain


class BaseSchema(pydantic.BaseModel):
    """Base data transfer object."""

    model_config = pydantic.ConfigDict(frozen=True)


class SampleReadSchema(BaseSchema):
    """Data transfer object for a sample."""

    id: str
    text: str
    text_class: Optional[str] = pydantic.Field(serialization_alias="textClass")
    text_class_predictions: Optional[tuple[float, ...]] = pydantic.Field(
        serialization_alias="textClassPredictions"
    )


class SamplePatchSchema(BaseSchema):
    """Data transfer object for a sample patch."""

    text: Optional[str] = None
    text_class: Optional[str] = pydantic.Field(validation_alias="textClass")


class TaskReadSchema(BaseSchema):
    """Data transfer object for a task config."""

    text_classes: tuple[str, ...] = pydantic.Field(serialization_alias="textClasses")
