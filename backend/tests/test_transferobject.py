"""Test suite for transfer objects."""

import pytest

from nlpanno import data, domain, worker
from nlpanno.server import status, transferobject


@pytest.mark.parametrize(
	"input_data, expected_output",
	[
		(worker.WorkerStatus(is_working=True), transferobject.WorkerStatusDTO(is_working=True)),
		(worker.WorkerStatus(is_working=False), transferobject.WorkerStatusDTO(is_working=False)),
	],
)
def test_worker_status_from_domain_object(
	input_data: worker.WorkerStatus, expected_output: transferobject.WorkerStatusDTO
) -> None:
	"""Test creating a worker status data transfer object from a domain object."""
	dto = transferobject.WorkerStatusDTO.from_domain_object(input_data)
	assert dto == expected_output


@pytest.mark.parametrize(
	"input_data, expected_output",
	[
		(
			status.Status(worker=worker.WorkerStatus(is_working=True)),
			transferobject.StatusDTO(worker=transferobject.WorkerStatusDTO(is_working=True)),
		),
		(
			status.Status(worker=worker.WorkerStatus(is_working=False)),
			transferobject.StatusDTO(worker=transferobject.WorkerStatusDTO(is_working=False)),
		),
	],
)
def test_status_from_domain_object(
	input_data: status.Status, expected_output: transferobject.StatusDTO
) -> None:
	"""Test creating a status data transfer object from a domain object."""
	dto = transferobject.StatusDTO.from_domain_object(input_data)
	assert dto == expected_output


@pytest.mark.parametrize(
	"input_data, expected_output",
	[
		(
			domain.Sample("id", "text", "text class", (0.1, 0.2)),
			transferobject.SampleDTO(
				id="id", text="text", text_class="text class", text_class_predictions=(0.1, 0.2)
			),
		),
		(
			domain.Sample("id", "text", "text class", None),
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
	dto = transferobject.SampleDTO.from_domain_object(input_data)
	assert dto == expected_output


@pytest.mark.parametrize(
	"input_data, expected_output",
	[
		(
			domain.TaskConfig(("class 1", "class 2")),
			transferobject.TaskConfigDTO(text_classes=("class 1", "class 2")),
		),
	],
)
def test_task_config_from_domain_object(
	input_data: domain.TaskConfig, expected_output: transferobject.TaskConfigDTO
) -> None:
	"""Test creating a task config data transfer object from a domain object."""
	dto = transferobject.TaskConfigDTO.from_domain_object(input_data)
	assert dto == expected_output
