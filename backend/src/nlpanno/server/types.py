import pydantic
from nlpanno import database
from typing import Optional, Tuple


def to_camel(string: str) -> str:
    string = ''.join(word.capitalize() for word in string.split('_'))
    string = string[0].lower() + string[1:]
    return string


class SamplePatch(pydantic.BaseModel):
    text: Optional[str] = None
    text_class: Optional[str] = None
    text_class_predictions: Optional[Tuple[float, ...]] = None

    class Config:
        alias_generator = to_camel
