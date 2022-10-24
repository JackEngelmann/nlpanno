import pydantic
from nlpanno import database
from typing import Optional, Tuple


class SamplePatch(pydantic.BaseModel):
    text: Optional[str] = None
    text_class: Optional[str] = None
    text_class_prediction: Optional[Tuple[float, ...]] = None
