import { useEffect, useState } from "react"
import { Sample, TaskConfig, Status } from "./types"

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
    const result = await fetch(url, options)
    if (!result.ok) {
        throw new Error(`Request failed (${result.status})`)
    }
    // TODO: could validate that result has expected format here.
    return await result.json()
}

export async function queryNextSample(): Promise<Sample> {
    return await fetchJson<Sample>("/api/nextSample")
}

export async function mutateSample(sample: Sample) {
    return await fetchJson<Sample>(`/api/samples/${sample.id}`, {
        method: "PATCH",
        body: JSON.stringify(sample),
        headers: { "Content-Type": "application/json" },
    })
}

async function queryTaskConfig(): Promise<TaskConfig> {
    return await fetchJson<TaskConfig>("/api/taskConfig")
}

async function queryStatus(): Promise<Status> {
    return await fetchJson<Status>("/api/status")
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
    update(sample: Sample): Promise<void>
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
        update,
        isLoading: samples.length === 0,
        errorOccurred
    }
}

type StatusQueryResult = {
    data: Status | null
    isLoading: boolean,
    errorOccurred: boolean
}

export function useStatus(pollIntervalMs: number): StatusQueryResult {
    const [status, setStatus] = useState<Status | null>(null)
    const [errorOccurred, setErrorOccurred] = useState(false)

    useEffect(() => {
        const interval = setInterval(async () => {
            try {
                const newStatus = await queryStatus()
                if (JSON.stringify(status) !== JSON.stringify(newStatus)) {
                    setStatus(newStatus)
                }
            } catch {
                setErrorOccurred(true)
            }
        }, pollIntervalMs)
        return () => clearInterval(interval)
    }, [setStatus])

    return {
        data: status,
        isLoading: !status,
        errorOccurred
    }
}
