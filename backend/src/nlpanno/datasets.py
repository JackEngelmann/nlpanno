"""Utilities for loading common datasets."""

import dataclasses
import pathlib
from collections.abc import Iterator

from nlpanno import data


@dataclasses.dataclass
class Dataset:
	"""Base class for datasets."""

	task_config: data.TaskConfig
	samples: tuple[data.Sample, ...]

	def fill_database(self, database: data.Database) -> None:
		"""Fill a database with the data from the dataset."""
		database.set_task_config(self.task_config)
		for sample in self.samples:
			database.add_sample(sample)


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
		samples, task_config = self._read_data()
		super().__init__(task_config, samples)

	def _read_data(self) -> tuple[tuple[data.Sample, ...], data.TaskConfig]:
		"""Load data from disk."""
		samples: list[data.Sample] = []
		text_classes: set[str] = set()
		for line in self._read_lines():
			if self._limit_hit(samples):
				break
			sample, text_class = self._parse_line(line)
			samples.append(sample)
			text_classes.add(text_class)
		task_config = data.TaskConfig(tuple(sorted(text_classes)))
		return tuple(samples), task_config

	def _limit_hit(self, samples: list[data.Sample]) -> bool:
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

	def _parse_line(self, line: str) -> tuple[data.Sample, str]:
		"""Parse a line from the data file."""
		_, text_class, _, text, *_ = line.split("\t")
		text_class = text_class[3:].replace("_", " ").lower()
		if self._add_class_to_text:
			text += f" ({text_class})"
		return data.Sample(data.create_id(), text, None), text_class
