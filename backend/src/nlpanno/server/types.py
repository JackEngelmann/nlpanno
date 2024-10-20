"""Type definitions for implementing the server/API."""

from typing import Optional

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
	text_class_predictions: Optional[tuple[float, ...]] = None

	# The alias is used so that the API is in camel case,
	# but the python code is in the usual casing
	# (lowercase, separated by underscores).
	model_config = pydantic.ConfigDict(alias_generator=to_camel)
