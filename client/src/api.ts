import { useEffect, useState } from "react"
import { Sample, AnnotationTask } from "./types"

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
    const result = await fetch(url, options)
    if (!result.ok) {
        throw new Error(`Request failed (${result.status})`)
    }
    // TODO: could validate that result has expected format here.
    return await result.json()
}

export async function queryTasks(): Promise<AnnotationTask[]> {
    return await fetchJson<AnnotationTask[]>("/api/tasks")
}

export async function queryNextSample(taskId: string): Promise<Sample> {
    return await fetchJson<Sample>(`/api/tasks/${taskId}/nextSample`)
}

export async function mutateSample(sample: Sample) {
    return await fetchJson<Sample>(`/api/samples/${sample.id}`, {
        method: "PATCH",
        body: JSON.stringify({
            id: sample.id,
            textClassId: sample.textClass?.id,
        }),
        headers: { "Content-Type": "application/json" },
    })
}

type TasksQueryResult = {
    data: AnnotationTask[] | null
    isLoading: boolean,
    errorOccurred: boolean
}

export function useTasks(): TasksQueryResult {
    const [tasks, setTasks] = useState<AnnotationTask[] | null>(null)
    const [errorOccurred, setErrorOccurred] = useState(false)

    useEffect(() => {
        let ignore = false

        queryTasks().then(tasks => {
            if (ignore) return
            setTasks(tasks)
        }).catch(() => setErrorOccurred(true))
        return () => {
            ignore = true
        }
    }, [])

    return {
        data: tasks,
        isLoading: !tasks,
        errorOccurred
    }
}

type SampleStreamResult = {
    data: Sample[]
    isLoading: boolean,
    errorOccurred: boolean
    loadNext(): Promise<void>
    update(sample: Sample): Promise<void>
}

export function useSampleStream(taskId: string): SampleStreamResult {
    const [samples, setSamples] = useState<Sample[]>([])
    const [errorOccurred, setErrorOccurred] = useState(false)

    async function loadNext() {
        try {
            const nextSample = await queryNextSample(taskId)
            setSamples(samples => [...samples, nextSample])
        } catch {
            setErrorOccurred(true)
        }
    }

    async function update(sample: Sample) {
        try {
            const mutated = await mutateSample(sample)
            setSamples(samples => samples.map(s => s.id === sample.id ? mutated : s))
        } catch {
            setErrorOccurred(true)
        }
    }

    // Load first sample.
    useEffect(() => {
        let ignore = false

        queryNextSample(taskId)
            .then(sample => {
                if (ignore) return
                setSamples([sample])
            }).catch(() => setErrorOccurred(true))
        return () => {
            // Ignore result when component is unmounted while waiting for the response.
            ignore = true
        }
    }, [])

    return {
        data: samples,
        loadNext,
        update,
        isLoading: samples.length === 0,
        errorOccurred
    }
}