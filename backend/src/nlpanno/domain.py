import uuid
import dataclasses
from typing import Optional

Id = str


def create_id() -> Id:
	"""Create unique identifier."""
	return str(uuid.uuid4())


@dataclasses.dataclass
class Sample:
	"""Data structure for a sample."""

	id: Id
	text: str
	text_class: Optional[str] = None
	text_class_predictions: Optional[tuple[float, ...]] = None


@dataclasses.dataclass
class TaskConfig:
	"""Data structure for a task configuration."""

	text_classes: tuple[str, ...]