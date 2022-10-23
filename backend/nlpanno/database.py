from typing import List, Optional, Tuple, TypedDict
import dataclasses
import abc
import uuid


Id = str


def create_id() -> Id:
    return str(uuid.uuid4())


@dataclasses.dataclass
class Sample:
    id: Id
    text: str
    text_class: Optional[str]


class FindCriteria(TypedDict, total=False):
    text_class: Optional[str]


class Database(abc.ABC):
    @abc.abstractclassmethod
    def add(self, sample: Sample) -> None:
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_id(self, id: Id) -> Sample:
        raise NotImplementedError()
    
    @abc.abstractclassmethod
    def find_all(self, criteria: Optional[FindCriteria]) -> Tuple[Sample, ...]:
        raise NotImplementedError()
    
    @abc.abstractclassmethod
    def update(self, sample: Sample) -> None:
        raise NotImplementedError()


class InMemoryDatabase(Database):
    def __init__(self) -> None:
        self._samples: List[Sample] = []

    def add(self, sample: Sample) -> None:
        self._samples.append(sample)

    def get_id(self, id: Id) -> Sample:
        for sample in self._samples:
            if sample.id == id:
                return sample
        raise ValueError(f"No sample with id {id}")
    
    def find_all(self, criteria: Optional[FindCriteria] = None) -> Tuple[Sample, ...]:
        if criteria is None:
            return tuple(self._samples)
        matches = []
        for sample in self._samples:
            text_class_matches = "text_class" not in criteria or sample.text_class == criteria['text_class']
            if text_class_matches:
                matches.append(sample)
        return tuple(matches)

    def update(self, sample: Sample) -> None:
        for old_sample in self._samples:
            if old_sample.id == sample.id:
                old_sample.text_class = sample.text_class
                break
