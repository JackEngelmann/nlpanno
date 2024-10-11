import { useReducer } from "react"
import { Sample, TaskConfig } from "./api"

type State = {
    currentIdx: number,
    samples: Sample[],
    taskConfig: TaskConfig | undefined,
}

type Action = {
    type: "selectedNextSample",
} | {
    type: "selectedPreviousSample"
} | {
    type: "updatedSample",
    sample: Sample,
} | {
    type: "loadedSample",
    sample: Sample,
} | {
    type: "loadedTaskConfig",
    taskConfig: TaskConfig,
}

const INITIAL_STATE: State = {
    currentIdx: 0,
    samples: [],
    taskConfig: undefined,
}

function reduce(state: State, action: Action): State {
    if (action.type === "selectedNextSample") {
        return {
            ...state,
            currentIdx: state.currentIdx + 1,
        }
    }
    if (action.type === "selectedPreviousSample") {
        return {
            ...state,
            currentIdx: state.currentIdx - 1,
        }
    }
    if (action.type === "updatedSample") {
        const updated = state.samples.map(
            sample => sample.id === action.sample.id ? action.sample : sample
        )
        return {
            ...state,
            samples: updated
        }
    }
    if (action.type === "loadedSample") {
        const samples = [...state.samples, action.sample]
        return {
            ...state,
            samples,
        }
    }
    if (action.type === "loadedTaskConfig") {
        return {
            ...state,
            taskConfig: action.taskConfig,
        }
    }

    // The purpose of this is to check for exhaustive handling
    // of all values for "type" at **compile time**.
    assertNever(action)

    return state
}

function assertNever(value: never) {
    throw new Error("Unexpected value: " + value);
}

export function useAppStateReducer() {
    const [state, dispatch] = useReducer(reduce, INITIAL_STATE)
    return [state, dispatch] as const
}