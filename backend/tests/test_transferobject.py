"""Test suite for transfer objects."""
import pytest

from nlpanno import data
from nlpanno.server import transferobject


@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        (
            data.Sample(
                "id",
                "text",
                "text class",
                (0.1, 0.2),
            ),
            transferobject.SampleDTO(
                id="id",
                text="text",
                textClass="text class",
                textClassPredictions=[0.1, 0.2],
            ),
        ),
        (
            data.Sample(
                "id",
                "text",
                "text class",
                None,
            ),
            transferobject.SampleDTO(
                id="id",
                text="text",
                textClass="text class",
                textClassPredictions=None,
            ),
        ),
        (
            (
                data.Sample(
                    "id",
                    "text",
                    "text class",
                    (0.1, 0.2),
                ),
            ),
            [
                transferobject.SampleDTO(
                    id="id",
                    text="text",
                    textClass="text class",
                    textClassPredictions=[0.1, 0.2],
                )
            ],
        ),
        (
            [
                data.Sample(
                    "id",
                    "text",
                    "text class",
                    (0.1, 0.2),
                ),
            ],
            [
                transferobject.SampleDTO(
                    id="id",
                    text="text",
                    textClass="text class",
                    textClassPredictions=[0.1, 0.2],
                )
            ],
        ),
        (
            data.TaskConfig(("class 1", "class 2")),
            transferobject.TaskConfigDTO(textClasses=["class 1", "class 2"]),
        ),
    ],
)
def test_to_dto(input_data, expected_output):
    """Test transforming domain objects to data transfer objects (DTOs)."""
    output = transferobject.to_dto(input_data)
    assert output == expected_output
