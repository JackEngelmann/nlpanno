from typing import List, Tuple
from nlpanno import database
import pathlib
import abc


class DatasetBuilder:
    @abc.abstractmethod
    def build(self, db: database.Database):
        raise NotImplementedError()
    

class MtopBuilder(DatasetBuilder):
    def __init__(self, path: pathlib.Path, add_class_to_text: bool = False) -> None:
        samples, text_classes = self._load_data(path, add_class_to_text)
        self._samples = samples
        self._text_classes = text_classes
    
    def _load_data(self, path: pathlib.Path, add_class_to_text: bool) -> Tuple[Tuple[database.Sample], Tuple[str]]:
        samples: List[database.Sample] = []
        text_classes: List[str] = []
        for file_name in ['eval.txt', 'test.txt', 'train.txt']:
            input_file_path = path.joinpath(file_name)
            with open(input_file_path, encoding='utf-8') as input_file:
                for line in input_file:
                    fields = line.split('\t')
                    text = fields[3]
                    text_class = self._format_text_class(fields[1])
                    text_classes.append(text_class)
                    if add_class_to_text:
                        text += f" ({text_class})"
                    sample = database.Sample(
                        database.create_id(),
                        text,
                        None
                    )
                    samples.append(sample)
        return tuple(samples), tuple(sorted(text_classes))
                    
    @staticmethod
    def _format_text_class(original: str) -> str:
        return original[3:].replace('_', ' ').lower()
    
    def build(self, db: database.Database):
        for sample in self._samples:
            db.add_sample(sample)
        task_config = database.TaskConfig(self._text_classes)
        db.set_task_config(task_config)
