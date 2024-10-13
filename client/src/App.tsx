import { useState } from "react";
import styles from "./App.module.css";
import { Sample, TaskConfig, useSampleStream, useTaskConfig } from './api';
import { ClassSelection } from './components/ClassSelection/ClassSelection';


function App() {
  const taskConfigState = useTaskConfig()
  const sampleStream = useSampleStream()

  const [selectedSampleIdx, setSelectedSampleIdx] = useState(0)
  const selectNextSample = () => setSelectedSampleIdx(selectedSampleIdx + 1)
  const selectPreviousSample = () => setSelectedSampleIdx(selectedSampleIdx - 1)

  const errorOccurred = taskConfigState.errorOccurred || sampleStream.errorOccurred
  if (errorOccurred) return <ErrorScreen />

  const isLoading = taskConfigState.isLoading || sampleStream.isLoading
  if (isLoading) return <LoadingScreen />

  const taskConfig = taskConfigState.data!
  const samples = sampleStream.data!
  const isFirstSample = selectedSampleIdx === 0
  const isLastSample = selectedSampleIdx === samples.length - 1
  const selectedSample = samples[selectedSampleIdx]
  const classPredictions = getSortedClassPredictions(selectedSample, taskConfig)

  async function onTextClassSelected(textClass: string) {
    // Update does not need to be awaited, can already move on to the next sample.
    sampleStream.patch({ id: selectedSample.id, textClass })
    if (isLastSample) await sampleStream.loadNext()
    selectNextSample()
  }

  function renderSampleSelector() {
    return (
      <div className={styles.selector}>
        <button onClick={selectPreviousSample} disabled={isFirstSample}>
          {"<"}
        </button>
        <span>{selectedSampleIdx + 1} / {samples.length}</span>
        <button onClick={selectNextSample} disabled={isLastSample}>
          {">"}
        </button>
      </div>
    )
  }

  return (
    <div className={styles.root}>
      <div className={styles.sample}>
        <div className={styles.text}>
          {selectedSample.text}
        </div>
        {renderSampleSelector()}
      </div>
      <ClassSelection
        className={styles.annotation}
        classPredictions={classPredictions}
        label={selectedSample.textClass || undefined}
        onChange={onTextClassSelected}
      />
    </div>
  );
}

type ClassPrediction = {
  className: string,
  value: number
}

function getSortedClassPredictions(sample: Sample, taskConfig: TaskConfig): ClassPrediction[] {
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

function LoadingScreen() {
  return (
    <div className={styles.root}>
      <div className={styles.loading}>Loading...</div>
    </div>
  )
}

function ErrorScreen() {
  return (
    <div className={styles.root}>
      <div className={styles.error}>{"An Error occurred :("}</div>
    </div>
  )
}

export default App;
