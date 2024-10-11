import { useEffect } from "react";
import styles from "./App.module.css";
import { loadNextSample, loadTaskConfig, Sample, TaskConfig, updateSample } from './api';
import { ClassSelection } from './components/ClassSelection/ClassSelection';
import { useAppStateReducer } from "./appState";

function App() {
  const [state, dispatch] = useAppStateReducer()

  // Initial Loading.
  useEffect(() => {
    console.log("initial loading")
    loadNextSample()
      .then(sample => dispatch({ "type": "loadedSample", sample }))

    loadTaskConfig()
      .then(taskConfig => dispatch({ "type": "loadedTaskConfig", taskConfig }))
  }, [dispatch])

  if (state.samples.length === 0 || !state.taskConfig) {
    return <span>Loading</span>
  }

  const isLastSample = state.currentIdx === state.samples.length - 1
  const isFirstSample = state.currentIdx === 0
  const currentSample = state.samples[state.currentIdx]
  const classPredictions = getSortedClassPredictions(currentSample, state.taskConfig)

  async function onTextClassSelected(textClass: string) {
    // Update does not need to be awaited, can already move on to the next sample.
    updateSample(currentSample.id, textClass)
      .then(sample => dispatch({ type: "updatedSample", sample }))

    if (isLastSample) {
      const nextSample = await loadNextSample()
      dispatch({ type: "loadedSample", sample: nextSample })
    }

    dispatch({ type: "selectedNextSample" })
  }

  function renderSampleSelector() {
    return (
      <div className={styles.selector}>
        <button
          onClick={() => dispatch({ type: "selectedPreviousSample" })}
          disabled={isFirstSample}
        >
          {"<"}
        </button>
        <span>{state.currentIdx + 1} / {state.samples.length}</span>
        <button
          onClick={() => dispatch({ type: "selectedNextSample" })}
          disabled={isLastSample}
        >
          {">"}
        </button>
      </div>
    )
  }

  return (
    <div className={styles.root}>
      <div className={styles.sample}>
        <div className={styles.text}>
          {currentSample.text}
        </div>
        {renderSampleSelector()}
      </div>
      <ClassSelection
        className={styles.annotation}
        classPredictions={classPredictions}
        label={currentSample.textClass || undefined}
        onChange={onTextClassSelected}
      />
    </div>
  );
}

function getSortedClassPredictions(sample: Sample, taskConfig: TaskConfig): { className: string, value: number }[] {
  if (!sample.textClassPredictions) {
    return taskConfig.textClasses.map(className => ({ className, value: 0 }))
  }

  const textClassPredictions = taskConfig.textClasses.map((className, classIndex) => ({
    className,
    value: sample.textClassPredictions![classIndex]
  }))
  console.log(textClassPredictions)

  // Sort by value (confidence prediction) in descending order.
  return textClassPredictions.sort((a, b) => b.value - a.value)
}

export default App;
