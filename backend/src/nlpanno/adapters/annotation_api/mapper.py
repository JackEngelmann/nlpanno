from nlpanno import domain

from . import schema


def map_sample_to_read_schema(
    sample: domain.Sample, task: domain.AnnotationTask
) -> schema.SampleReadSchema:
    """Map a sample to a read schema."""
    # TODO: include task in domain object.
    confidence_by_class = {
        estimate.text_class: estimate.confidence for estimate in sample.estimates
    }
    text_class_predictions = tuple(
        confidence_by_class.get(text_class, 0.0) for text_class in task.text_classes
    )
    return schema.SampleReadSchema(
        id=sample.id,
        text=sample.text,
        text_class=sample.text_class,
        text_class_predictions=text_class_predictions,
    )


def map_task_to_read_schema(
    task_config: domain.AnnotationTask,
) -> schema.TaskReadSchema:
    """Map a task to a read schema."""
    return schema.TaskReadSchema(
        text_classes=task_config.text_classes,
    )
