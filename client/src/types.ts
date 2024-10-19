export type Sample = {
    id: string
    text: string
    textClass: string | null
    textClassPredictions: number[] | null
}

export type TaskConfig = {
    textClasses: string[]
}

export type Status = {
    worker: {
        isWorking: boolean
    }
}