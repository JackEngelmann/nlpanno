"""Type definitions for implementing the server/API."""

# pylint: disable = too-few-public-methods

from typing import Optional, Tuple

import pydantic


def to_camel(string: str) -> str:
    """Transform a string to camel casing."""
    string = "".join(word.capitalize() for word in string.split("_"))
    string = string[0].lower() + string[1:]
    return string


class SamplePatch(pydantic.BaseModel):
    """Input to patch (partial update) a sample."""

    text: Optional[str] = None
    text_class: Optional[str] = None
    text_class_predictions: Optional[Tuple[float, ...]] = None

    class Config:
        """Pydantic config."""

        # The alias is used so that the API is in camel case,
        # but the python code is in the usual casing
        # (lowercase, separated by underscores).
        alias_generator = to_camel
