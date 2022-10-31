import pytest
from nlpanno.server import transferobject
from nlpanno import database


@pytest.mark.parametrize("input, expected_output", [
    (
        database.Sample(
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
        )
    ),
    (
        database.Sample(
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
        )
    ),
    (
        (
            database.Sample(
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
            database.Sample(
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
        database.TaskConfig(("class 1", "class 2")),
        transferobject.TaskConfigDTO(textClasses=["class 1", "class 2"])
    )
])
def test_to_transfer_object(input, expected_output):
    output = transferobject.to_dto(input)
    assert output == expected_output
