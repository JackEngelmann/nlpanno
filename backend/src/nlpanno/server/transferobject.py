from typing import Any, Optional, List
import pydantic
from nlpanno import database
import functools


class SampleDTO(pydantic.BaseModel, extra=pydantic.Extra.forbid):
    id: str
    text: str
    textClass: Optional[str]
    textClassPredictions: Optional[List[float]]

    @classmethod
    def from_domain_object(cls, domain_object: database.Sample):
        return cls(
            id=domain_object.id,
            text=domain_object.text,
            textClass=domain_object.text_class,
            textClassPredictions=domain_object.text_class_predictions,
        )


class TaskConfigDTO(pydantic.BaseModel, extra=pydantic.Extra.forbid):
    textClasses: List[str]

    @classmethod
    def from_domain_object(cls, domain_object: database.TaskConfig):
        return cls(
            textClasses=domain_object.text_classes
        )


@functools.singledispatch
def to_dto(domain_object: Any):
    raise TypeError(f"type {type(domain_object)} it not supported by the 'to_dto' function.")

@to_dto.register
def _(domain_object: database.Sample):
    return SampleDTO.from_domain_object(domain_object)

@to_dto.register
def _(domain_object: database.TaskConfig):
    return TaskConfigDTO.from_domain_object(domain_object)

@to_dto.register
def _(domain_object: tuple):
    return list(to_dto(d) for d in domain_object)

@to_dto.register
def _(domain_object: list):
    return list(to_dto(d) for d in domain_object)