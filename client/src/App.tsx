import { useState } from "react";
import styles from "./App.module.css";
import { useSampleStream, useTaskConfig } from './api';
import { ClassSelection } from './components/ClassSelection/ClassSelection';
import { Selector } from "./components/Selector/Selector";
import { LoadingScreen } from "./components/LoadingScreen/LoadingScreen";
import { ErrorScreen } from "./components/ErrorScreen/ErrorScreen";
import { getSortedClassPredictions } from "./classpredictions";

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
    if (isLastSample) await sampleStream.loadNext()
    selectNextSample()
    const updatedSample = { ...selectedSample, textClass }
    await sampleStream.update(updatedSample)
  }

  return (
    <div className={styles.root}>
      <div className={styles.sample}>
        <div className={styles.text}>
          {selectedSample.text}
        </div>
        <Selector
          isFirst={isFirstSample}
          isLast={isLastSample}
          current={selectedSampleIdx}
          total={samples.length}
          onPrevious={selectPreviousSample}
          onNext={selectNextSample}
        />
      </div>
      <ClassSelection
        key={selectedSample.id}
        className={styles.annotation}
        classPredictions={classPredictions}
        label={selectedSample.textClass || undefined}
        onChange={onTextClassSelected}
      />
    </div>
  );
}

export default App;
