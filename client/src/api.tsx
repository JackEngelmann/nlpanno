export type Sample = {
    id: string
    text: string
    textClass: string | null
    textClassPredictions: number[] | null
}

export type TaskConfig = {
    textClasses: string[]
}

export async function loadNextSample(): Promise<Sample> {
    const result = await fetch("/nextSample")
    return await result.json()
}

export async function updateSample(id: string, textClass: string | null) {
    const result = await fetch(`/samples/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ textClass }),
        headers: {
            "Content-Type": "application/json",
        },
    });
    const jsonResult = await result.json();
    return jsonResult;
}

export async function loadTaskConfig(): Promise<TaskConfig> {
    const result = await fetch("/taskConfig")
    return await result.json()
}
