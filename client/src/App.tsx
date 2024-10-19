import { useState } from "react";
import styles from "./App.module.css";
import { useSampleStream, useTaskConfig, useStatus } from './api';
import { ClassSelection } from './components/ClassSelection/ClassSelection';
import { StatusIndicator } from "./components/StatusIndicator/StatusIndicator";
import { Selector } from "./components/Selector/Selector";
import { LoadingScreen } from "./components/LoadingScreen/LoadingScreen";
import { ErrorScreen } from "./components/ErrorScreen/ErrorScreen";
import { getSortedClassPredictions } from "./classpredictions";

function App() {
  const taskConfigState = useTaskConfig()
  const sampleStream = useSampleStream()
  const statusQueryResult = useStatus(1000)

  const [selectedSampleIdx, setSelectedSampleIdx] = useState(0)
  const selectNextSample = () => setSelectedSampleIdx(selectedSampleIdx + 1)
  const selectPreviousSample = () => setSelectedSampleIdx(selectedSampleIdx - 1)

  const errorOccurred = taskConfigState.errorOccurred || sampleStream.errorOccurred || statusQueryResult.errorOccurred
  if (errorOccurred) return <ErrorScreen />

  const isLoading = taskConfigState.isLoading || sampleStream.isLoading || statusQueryResult.isLoading
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

  return (
    <div className={styles.root}>
      <div className={styles.sample}>
        <div className={styles.text}>
          {selectedSample.text}
        </div>
        <StatusIndicator isWorking={statusQueryResult.data!.worker.isWorking} />
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
        className={styles.annotation}
        classPredictions={classPredictions}
        label={selectedSample.textClass || undefined}
        onChange={onTextClassSelected}
      />
    </div>
  );
}

export default App;
