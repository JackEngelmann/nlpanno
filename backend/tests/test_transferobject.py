"""Test suite for transfer objects."""

import pytest

from nlpanno import domain
from nlpanno.annotation import transferobject


@pytest.mark.parametrize(
	"input_data, expected_output",
	[
		(
			domain.Sample("id", "text", "text class"),
			transferobject.SampleDTO(
				id="id", text="text", text_class="text class", text_class_predictions=None
			),
		),
	],
)
def test_sample_from_domain_object(
	input_data: domain.Sample, expected_output: transferobject.SampleDTO
) -> None:
	"""Test creating a sample data transfer object from a domain object."""
	dto = transferobject.SampleDTO.from_domain_object(input_data, None)
	assert dto == expected_output


@pytest.mark.parametrize(
	"input_data, expected_output",
	[
		(
			domain.AnnotationTask(("class 1", "class 2")),
			transferobject.TaskConfigDTO(text_classes=("class 1", "class 2")),
		),
	],
)
def test_task_config_from_domain_object(
	input_data: domain.AnnotationTask, expected_output: transferobject.TaskConfigDTO
) -> None:
	"""Test creating a task config data transfer object from a domain object."""
	dto = transferobject.TaskConfigDTO.from_domain_object(input_data)
	assert dto == expected_output
