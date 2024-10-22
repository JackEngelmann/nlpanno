import pathlib

import pytest

from nlpanno import data, datasets

# This sample is from the [MTOP dataset](https://arxiv.org/abs/2008.09335).
_MTOP_LINE = """3232353833393435	IN:GET_MESSAGE	6:9:SL:RECIPIENT,10:13:SL:SENDER,18:23:SL:SENDER,24:29:SL:DATE_TIME	Haben mir Ben und Leroy heute geschrieben	messaging	de_XX	[IN:GET_MESSAGE [SL:SENDER Ben ] [SL:SENDER Leroy ] [SL:RECIPIENT mir ] [SL:DATE_TIME heute ] ]	{"tokens":["Haben","mir","Ben","und","Leroy","heute","geschrieben"],"tokenSpans":[{"start":0,"length":5},{"start":6,"length":3},{"start":10,"length":3},{"start":14,"length":3},{"start":18,"length":5},{"start":24,"length":5},{"start":30,"length":11}]}"""  # noqa: E501
_MTOP_TEXT_CLASS = "get message"
_MTOP_TEXT = "Haben mir Ben und Leroy heute geschrieben"


class TestMtop:
	"""Tests for the MTOP dataset."""

	@pytest.fixture
	def input_dir(self, tmp_path: pathlib.Path) -> pathlib.Path:
		"""Path to the input directory."""
		with open(tmp_path / "eval.txt", "w") as file:
			file.write(_MTOP_LINE)
			file.write("\n")
		return tmp_path

	def test_initiation(self, input_dir: pathlib.Path) -> None:
		"""Test initiation of the MTOP dataset."""
		dataset = datasets.MTOP(input_dir)
		assert len(dataset.samples) == 1
		assert dataset.samples[0].text == _MTOP_TEXT
		# Ground truth should be None, so that the user can annotate it.
		assert dataset.samples[0].text_class is None
		assert dataset.task_config.text_classes == (_MTOP_TEXT_CLASS,)

	def test_initiation_with_classname(self, input_dir: pathlib.Path) -> None:
		"""Test initiation of the MTOP dataset with class name."""
		dataset = datasets.MTOP(input_dir, add_class_to_text=True)
		assert len(dataset.samples) == 1
		assert dataset.samples[0].text == f"{_MTOP_TEXT} ({_MTOP_TEXT_CLASS})"
