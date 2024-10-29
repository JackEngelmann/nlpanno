import { useState } from "react";
import styles from "./AnnotationScreen.module.css";
import { useSampleStream, useTaskConfig } from '../api';
import { ClassSelection } from '../components/ClassSelection/ClassSelection';
import { Selector } from "../components/Selector/Selector";
import { LoadingScreen } from "../components/LoadingScreen/LoadingScreen";
import { ErrorScreen } from "../components/ErrorScreen/ErrorScreen";
import { getSortedClassPredictions } from "../classpredictions";
import { useParams } from "react-router-dom";
import { AvailableTextClass, TextClass } from "../types";

export function AnnotationScreen() {
  console.log("test")
  const { taskId } = useParams()
  console.log(taskId)
  const sampleStream = useSampleStream(taskId!)

  const [selectedSampleIdx, setSelectedSampleIdx] = useState(0)
  const selectNextSample = () => setSelectedSampleIdx(selectedSampleIdx + 1)
  const selectPreviousSample = () => setSelectedSampleIdx(selectedSampleIdx - 1)

  const errorOccurred = sampleStream.errorOccurred
  if (errorOccurred) return <ErrorScreen />

  const isLoading = sampleStream.isLoading
  if (isLoading) return <LoadingScreen />

  const samples = sampleStream.data!
  console.log(samples)
  const isFirstSample = selectedSampleIdx === 0
  const isLastSample = selectedSampleIdx === samples.length - 1
  const selectedSample = samples[selectedSampleIdx]
  async function onTextClassSelected(textClass: TextClass) {
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
        label={selectedSample.textClass || undefined}
        availableTextClasses={selectedSample.availableTextClasses}
        onChange={onTextClassSelected}
      />
    </div>
  );
}

