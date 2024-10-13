import { error } from "console"
import { useEffect, useState } from "react"

export type Sample = {
    id: string
    text: string
    textClass: string | null
    textClassPredictions: number[] | null
}

export type TaskConfig = {
    textClasses: string[]
}

export async function queryNextSample(): Promise<Sample> {
    const result = await fetch("/nextSample")
    if (!result.ok) {
        throw new Error(`Request failed (${result.status})`)
    }
    // TODO: could validate that result has expected format here.
    return await result.json()
}

type PatchSampleInput = {
    id: string,
    text?: string
    textClass?: string | null
    textClassPredictions?: number[] | null
}

export async function mutateSample(patchInput: PatchSampleInput) {
    const result = await fetch(`/samples/${patchInput.id}`, {
        method: "PATCH",
        body: JSON.stringify(patchInput),
        headers: { "Content-Type": "application/json" },
    });
    if (!result.ok) {
        throw new Error(`Request failed (${result.status})`)
    }
    // TODO: could validate that result has expected format here.
    return await result.json()
}

async function queryTaskConfig(): Promise<TaskConfig> {
    const result = await fetch("/taskConfig")
    if (!result.ok) {
        throw new Error(`Request failed (${result.status})`)
    }
    // TODO: could validate that result has expected format here.
    return await result.json()
}

type TaskConfigQueryResult = {
    data: TaskConfig | null
    isLoading: boolean,
    errorOccurred: boolean
}

export function useTaskConfig(): TaskConfigQueryResult {
    const [taskConfig, setTaskConfig] = useState<TaskConfig | null>(null)
    const [errorOccurred, setErrorOccurred] = useState(false)

    useEffect(() => {
        let ignore = false

        queryTaskConfig()
            .then(taskConfig => {
                if (ignore) return
                setTaskConfig(taskConfig)
            }).catch(() => setErrorOccurred(true))
        return () => {
            // Ignore result when component is unmounted while waiting for the response.
            ignore = true
        }
    }, [])

    return {
        isLoading: !taskConfig,
        errorOccurred,
        data: taskConfig
    }
}

type SampleStreamResult = {
    data: Sample[]
    isLoading: boolean,
    errorOccurred: boolean
    loadNext(): Promise<void>
    patch(patchInput: PatchSampleInput): Promise<void>
}

export function useSampleStream(): SampleStreamResult {
    const [samples, setSamples] = useState<Sample[]>([])
    const [errorOccurred, setErrorOccurred] = useState(false)

    async function loadNext() {
        try {
            const nextSample = await queryNextSample()
            setSamples(samples => [...samples, nextSample])
        } catch {
            setErrorOccurred(true)
        }
    }

    async function patch(patchInput: PatchSampleInput) {
        try {
            const mutated = await mutateSample(patchInput)
            setSamples(samples => samples.map(s => s.id === patchInput.id ? mutated : s))
        } catch {
            setErrorOccurred(true)
        }
    }

    // Load first sample.
    useEffect(() => {
        let ignore = false

        queryNextSample()
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
        patch,
        isLoading: samples.length === 0,
        errorOccurred
    }
}
