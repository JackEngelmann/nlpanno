import dataclasses
import uuid
from typing import Optional, Self

import torch

Id = str
Embedding = torch.Tensor


def create_id() -> Id:
	"""Create unique identifier."""
	return str(uuid.uuid4())


@dataclasses.dataclass
class Entity:
	"""Base class for all entities."""
	id: Optional[Id]


@dataclasses.dataclass
class TextClass(Entity):
	"""Data structure for a text class."""

	name: str


@dataclasses.dataclass
class ClassEstimate:
	"""Data structure for a class estimate."""

	text_class: TextClass
	confidence: float

	def update(self, confidence: float) -> None:
		self.confidence = confidence
	
	@classmethod
	def create(cls, text_class: TextClass, confidence: float) -> Self:
		return cls(text_class=text_class, confidence=confidence)


@dataclasses.dataclass
class AnnotationTask:
	"""Data structure for task metadata."""

	text_classes: tuple[TextClass, ...]
	# TODO: add samples?
	# Would need to find a solution not to load all samples in memory.


@dataclasses.dataclass
class Sample(Entity):
	"""Data structure for a sample."""

	text: str
	text_class: Optional[TextClass] = None
	embedding: Optional[Embedding] = None
	estimates: tuple[ClassEstimate, ...] = ()

	@classmethod
	def create(cls, text: str) -> Self:
		return cls(text=text)

	def annotate(self, text_class: TextClass) -> None:
		# TODO: Add annotation service that checks that the text class is valid.
		self.text_class = text_class

	def embed(self, embedding: Embedding) -> None:
		self.embedding = embedding
	
	def add_class_estimate(self, class_estimate: ClassEstimate) -> None:
		for existing_class_estimate in self.estimates:
			if existing_class_estimate.text_class == class_estimate.text_class:
				existing_class_estimate.update(class_estimate.confidence)
				return
		self.estimates = self.estimates + (class_estimate,)
	
	def add_class_estimates(self, class_estimates: tuple[ClassEstimate, ...]) -> None:
		for class_estimate in class_estimates:
			self.add_class_estimate(class_estimate)
