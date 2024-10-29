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


class AvailableTextClassReadSchema(TextClassReadSchema):
    """Data transfer object for a text class that is available for annotation."""

    id: str
    name: str
    confidence: float


class SampleReadSchema(BaseSchema):
    """Data transfer object for a sample."""

    id: str
    text: str
    text_class: Optional[TextClassReadSchema] = pydantic.Field(serialization_alias="textClass")
    available_text_classes: Optional[tuple[AvailableTextClassReadSchema, ...]] = pydantic.Field(
        serialization_alias="availableTextClasses"
    )


class SamplePatchSchema(BaseSchema):
    """Data transfer object for a sample patch."""

    text_class_id: Optional[str] = pydantic.Field(validation_alias="textClassId")


class TaskReadSchema(BaseSchema):
    """Data transfer object for a task config."""

    id: str
    name: str
    text_classes: tuple[TextClassReadSchema, ...] = pydantic.Field(
        serialization_alias="textClasses"
    )
