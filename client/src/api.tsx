import { useCallback, useEffect, useState } from "react"

export type Sample = {
    id: string
    text: string
    textClass: string | null
    textClassPredictions: number[] | null
}

export type TaskConfig = {
    textClasses: string[]
}

async function getNextSample(): Promise<Sample> {
    const result = await fetch("/nextSample")
    return await result.json()
}

async function updateSample(id: string, textClass: string | null) {
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

async function getTaskConfig(): Promise<TaskConfig> {
    const result = await fetch("/taskConfig")
    return await result.json()
}

export function useSampleStream(): [Sample[] | undefined, () => void, (id: string, textClass: string | null) => void] {
    const [count, setCount] = useState(0)
    const [samples, setSamples] = useState<Sample[]>()
    useEffect(() => {
        getNextSample().then(nextSample => setSamples(samples => [...(samples || []), nextSample]))
    }, [count])
    const getNext = useCallback(() => setCount(count => count + 1), [])
    const updateSampleInStream = useCallback(
        (id: string, textClass: string | null) => {
            updateSample(id, textClass).then(updated => {
                setSamples(samples => {
                    if (!samples) return undefined
                    return samples.map(s => s.id === id ? updated : s)
                })
            })
        },
        [],
    )
    return [samples, getNext, updateSampleInStream]
}

export function useTaskConfig(): TaskConfig | undefined {
    const [taskConfig, setTaskConfig] = useState<TaskConfig>()
    useEffect(() => {
        getTaskConfig().then(taskConfig => setTaskConfig(taskConfig))
    }, [])
    return taskConfig
}
