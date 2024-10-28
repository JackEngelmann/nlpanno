"""Schemas for the API."""

from typing import Optional

import pydantic


class BaseSchema(pydantic.BaseModel):
    """Base data transfer object."""

    model_config = pydantic.ConfigDict(frozen=True)


class TextClassReadSchema(BaseSchema):
    """Data transfer object for a text class."""

    id: str
    name: str


class SampleReadSchema(BaseSchema):
    """Data transfer object for a sample."""

    id: str
    text: str
    text_class: Optional[TextClassReadSchema] = pydantic.Field(serialization_alias="textClass")
    text_class_predictions: Optional[tuple[float, ...]] = pydantic.Field(
        serialization_alias="textClassPredictions"
    )


class SamplePatchSchema(BaseSchema):
    """Data transfer object for a sample patch."""

    text_class_id: Optional[str] = pydantic.Field(validation_alias="textClassId")


class TaskReadSchema(BaseSchema):
    """Data transfer object for a task config."""

    id: str
    text_classes: tuple[TextClassReadSchema, ...] = pydantic.Field(
        serialization_alias="textClasses"
    )
