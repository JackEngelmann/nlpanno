"""Utilities for loading common datasets."""

import dataclasses
import logging
import pathlib
from collections.abc import Iterator

from nlpanno.domain import model

_LOG = logging.getLogger("nlpanno")


@dataclasses.dataclass
class Dataset:
    """Base class for datasets."""

    task_config: model.AnnotationTask
    samples: tuple[model.Sample, ...]


class MTOP(Dataset):
    """
    Dataset builder for the MTOP dataset.

    https://aclanthology.org/2021.eacl-main.257/
    """

    def __init__(
        self, path: pathlib.Path | str, add_class_to_text: bool = False, limit: int | None = None
    ) -> None:
        self._add_class_to_text = add_class_to_text
        self._limit = limit
        self._path = path if isinstance(path, pathlib.Path) else pathlib.Path(path)
        if not self._path.exists():
            raise ValueError(f"Path does not exist: '{self._path}'")
        samples, task_config = self._read_data()
        _LOG.info(f"Samples: {len(samples)}")
        super().__init__(task_config, samples)

    def _read_data(self) -> tuple[tuple[model.Sample, ...], model.AnnotationTask]:
        """Load data from disk."""
        annotation_task = model.AnnotationTask.create("MTOP")
        samples: list[model.Sample] = []
        text_classes: set[str] = set()
        for line in self._read_lines():
            _LOG.info(f"Line: {line}")
            if self._limit_hit(samples):
                break
            text, text_class = self._parse_line(line)
            sample = model.Sample.create(
                annotation_task_id=annotation_task.id,
                text=text,
            )
            samples.append(sample)
            text_classes.add(text_class)
        sorted_text_classes = tuple(sorted(text_classes))
        for text_class in sorted_text_classes:
            annotation_task.create_text_class(text_class)
        return tuple(samples), annotation_task

    def _limit_hit(self, samples: list[model.Sample]) -> bool:
        """Check if the limit has been hit."""
        if self._limit is None:
            return False
        return len(samples) >= self._limit

    def _read_lines(self) -> Iterator[str]:
        """Read lines from the given file."""
        data_file_paths = list(self._path.glob("*.txt"))
        for data_file_path in data_file_paths:
            with open(data_file_path, encoding="utf-8") as input_file:
                yield from input_file

    def _parse_line(self, line: str) -> tuple[str, str]:
        """Parse a line from the data file."""
        _, text_class, _, text, *_ = line.split("\t")
        text_class = text_class[3:].replace("_", " ").lower()
        if self._add_class_to_text:
            text += f" ({text_class})"
        return text, text_class
