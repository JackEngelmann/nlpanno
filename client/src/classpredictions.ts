import { Sample, AnnotationTask } from "./types";

type ClassPrediction = {
    className: string,
    value: number
}

export function getSortedClassPredictions(sample: Sample, taskConfig: AnnotationTask): ClassPrediction[] {
    const classNames = taskConfig.textClasses

    // If there are no predictions, score each class as 0.
    if (!sample.textClassPredictions) {
        return classNames.map(className => ({ className, value: 0 }))
    }

    const predictions = classNames.map((className, classIndex) => ({
        className,
        value: sample.textClassPredictions![classIndex]
    }))

    // Sort by prediction score in descending order.
    return predictions.sort((a, b) => b.value - a.value)
}
