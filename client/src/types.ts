export type AvailableTextClass = {
    id: string
    name: string
    confidence: number
}

export type TextClass = {
    id: string
    name: string
}

export type Sample = {
    id: string
    text: string
    textClass: TextClass | null
    availableTextClasses: AvailableTextClass[]
}

export type AnnotationTask = {
    id: string
    name: string
    textClasses: string[]
}

export type Status = {
    worker: {
        isWorking: boolean
    }
}