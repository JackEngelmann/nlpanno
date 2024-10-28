from nlpanno.domain import model

from . import schema


def map_text_class_to_read_schema(text_class: model.TextClass) -> schema.TextClassReadSchema:
    """Map a text class to a read schema."""
    return schema.TextClassReadSchema(
        id=text_class.id,
        name=text_class.name,
    )


def map_sample_to_read_schema(
    sample: model.Sample, task: model.AnnotationTask
) -> schema.SampleReadSchema:
    """Map a sample to a read schema."""
    # TODO: include task in domain object.
    confidence_by_class = {
        estimate.text_class_id: estimate.confidence for estimate in sample.estimates
    }
    text_class_predictions = tuple(
        confidence_by_class.get(text_class.id, 0.0) for text_class in task.text_classes
    )
    text_class_read_schema = (
        map_text_class_to_read_schema(sample.text_class) if sample.text_class else None
    )
    return schema.SampleReadSchema(
        id=sample.id,
        text=sample.text,
        text_class=text_class_read_schema,
        text_class_predictions=text_class_predictions,
    )


def map_task_to_read_schema(
    annotation_task: model.AnnotationTask,
) -> schema.TaskReadSchema:
    """Map a task to a read schema."""
    return schema.TaskReadSchema(
        id=annotation_task.id,
        text_classes=tuple(
            map_text_class_to_read_schema(text_class) for text_class in annotation_task.text_classes
        ),
    )
