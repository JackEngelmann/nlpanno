from typing import Dict, List, Optional, Tuple, TypedDict
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
    text_class: Optional[str] = None
    text_class_predictions: Optional[Tuple[float, ...]] = None


class FindCriteria(TypedDict, total=False):
    text_class: Optional[str]


@dataclasses.dataclass
class TaskConfig:
    text_classes: Tuple[str, ...]


class Database(abc.ABC):
    @abc.abstractclassmethod
    def get_task_config(self) -> TaskConfig:
        raise NotImplementedError()
    
    @abc.abstractclassmethod
    def set_task_config(self, task_config: TaskConfig):
        raise NotImplementedError()

    @abc.abstractclassmethod
    def add_sample(self, sample: Sample) -> None:
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_sample_by_id(self, id: Id) -> Sample:
        raise NotImplementedError()
    
    @abc.abstractclassmethod
    def find_samples(self, criteria: Optional[FindCriteria]) -> Tuple[Sample, ...]:
        raise NotImplementedError()
    
    @abc.abstractclassmethod
    def update_sample(self, sample: Sample) -> None:
        raise NotImplementedError()


class InMemoryDatabase(Database):
    def __init__(self) -> None:
        self._sample_by_id: Dict[str, Sample] = {}
        self._task_config: Optional[TaskConfig] = None

    def get_task_config(self) -> TaskConfig:
        if self._task_config is None:
            raise RuntimeError('Task config was not set.')
        return self._task_config
    
    def set_task_config(self, task_config: TaskConfig):
        self._task_config = task_config

    def add_sample(self, sample: Sample) -> None:
        self._sample_by_id[sample.id] = sample

    def get_sample_by_id(self, id: Id) -> Sample:
        sample = self._sample_by_id.get(id)
        if sample is None:
            raise ValueError(f"No sample with id {id}")
        return sample
    
    def find_samples(self, criteria: Optional[FindCriteria] = None) -> Tuple[Sample, ...]:
        if criteria is None:
            return tuple(self._sample_by_id.values())
        matches = []
        for sample in self._sample_by_id.values():
            text_class_matches = "text_class" not in criteria or sample.text_class == criteria["text_class"]
            if text_class_matches:
                matches.append(sample)
        return tuple(matches)

    def update_sample(self, sample: Sample) -> None:
        # TODO: refactor
        self._sample_by_id[sample.id] = sample
