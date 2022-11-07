"""Utilities for loading common datasets."""
# pylint: disable = too-few-public-methods
import abc
import pathlib
from typing import List, Set, Tuple

from nlpanno import data


class DatasetBuilder:
    """Base class for dataset builders."""

    @abc.abstractmethod
    def build(self, database: data.Database):
        """Fill the database."""
        raise NotImplementedError()


class MtopBuilder(DatasetBuilder):
    """
    Dataset builder for the MTOP dataset.

    https://aclanthology.org/2021.eacl-main.257/
    """

    def __init__(self, path: pathlib.Path, add_class_to_text: bool = False) -> None:
        samples, text_classes = self._load_data(path, add_class_to_text)
        self._samples = samples
        self._text_classes = text_classes

    def _load_data(
        self, path: pathlib.Path, add_class_to_text: bool
    ) -> Tuple[Tuple[data.Sample, ...], Tuple[str, ...]]:
        """Load data from disk."""
        samples: List[data.Sample] = []
        text_classes: Set[str] = set()
        for file_name in ["eval.txt", "test.txt", "train.txt"]:
            input_file_path = path.joinpath(file_name)
            with open(input_file_path, encoding="utf-8") as input_file:
                for line in input_file:
                    fields = line.split("\t")
                    text = fields[3]
                    text_class = self._format_text_class(fields[1])
                    text_classes.add(text_class)
                    if add_class_to_text:
                        text += f" ({text_class})"
                    sample = data.Sample(data.create_id(), text, None)
                    samples.append(sample)
        return tuple(samples), tuple(sorted(text_classes))

    @staticmethod
    def _format_text_class(original: str) -> str:
        """Format text class to make it more readable."""
        return original[3:].replace("_", " ").lower()

    def build(self, database: data.Database) -> None:
        """Fill the database."""
        for sample in self._samples:
            database.add_sample(sample)
        task_config = data.TaskConfig(self._text_classes)
        database.set_task_config(task_config)
