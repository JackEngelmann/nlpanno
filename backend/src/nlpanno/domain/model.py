import dataclasses
import uuid
from typing import Optional, Self

import torch

Id = str
Embedding = torch.Tensor


# TODO: Move to another place.
def create_id() -> Id:
    """Create unique identifier."""
    return str(uuid.uuid4())


@dataclasses.dataclass
class Entity:
    """Base class for all entities."""

    id: Id


@dataclasses.dataclass
class TextClass(Entity):
    """Data structure for a text class."""

    name: str
    annotation_task_id: Id

    @classmethod
    def create(cls, name: str, annotation_task_id: Id) -> Self:
        return cls(id=create_id(), name=name, annotation_task_id=annotation_task_id)


@dataclasses.dataclass
class ClassEstimate(Entity):
    """Data structure for a class estimate."""

    text_class_id: Id
    confidence: float

    def update(self, confidence: float) -> None:
        self.confidence = confidence

    @classmethod
    def create(cls, text_class_id: Id, confidence: float) -> Self:
        return cls(id=create_id(), text_class_id=text_class_id, confidence=confidence)


@dataclasses.dataclass
class AnnotationTask(Entity):
    """Data structure for task metadata."""

    text_classes: tuple[TextClass, ...] = ()
    # TODO: add samples?
    # Would need to find a solution not to load all samples in memory.

    def get_text_class_by_id(self, id_: Id) -> TextClass:
        for text_class in self.text_classes:
            if text_class.id == id_:
                return text_class
        raise ValueError(f"Text class with id {id_} not found.")

    @classmethod
    def create(cls) -> Self:
        return cls(id=create_id(), text_classes=())

    def create_text_class(self, name: str) -> TextClass:
        text_class = TextClass.create(name, self.id)
        self.text_classes = self.text_classes + (text_class,)
        return text_class


@dataclasses.dataclass
class Sample(Entity):
    """Data structure for a sample."""

    annotation_task_id: Id
    text: str
    text_class: Optional[TextClass] = None
    embedding: Optional[Embedding] = None
    estimates: tuple[ClassEstimate, ...] = ()

    @classmethod
    def create(cls, annotation_task_id: Id, text: str) -> Self:
        return cls(id=create_id(), annotation_task_id=annotation_task_id, text=text)

    def annotate(self, text_class: TextClass | None) -> None:
        # TODO: Add annotation service that checks that the text class is valid.
        self.text_class = text_class

    def remove_label(self) -> None:
        self.text_class = None

    def embed(self, embedding: Embedding) -> None:
        self.embedding = embedding

    def add_class_estimate(self, class_estimate: ClassEstimate) -> None:
        for existing_class_estimate in self.estimates:
            if existing_class_estimate.text_class_id == class_estimate.text_class_id:
                existing_class_estimate.update(class_estimate.confidence)
                return
        self.estimates = self.estimates + (class_estimate,)

    def add_class_estimates(self, class_estimates: tuple[ClassEstimate, ...]) -> None:
        for class_estimate in class_estimates:
            self.add_class_estimate(class_estimate)
