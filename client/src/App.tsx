import './App.css';
import { Sample, TaskConfig, useSampleStream, useTaskConfig } from './api';
import { ClassSelection } from './components/ClassSelection/ClassSelection';
import { useState } from 'react';

function App() {
  // The samples are "streamed", so they are loaded one sample at the time.
  // This allows a dynamic order of the samples. Your past annotations may
  // influence which samples should be annotated next (e.g. active learning).
  const [samples, getNext, updateSample] = useSampleStream()

  // This offset allows going back in the stream (e.g. user makes a mistake
  // and wants to fix the previous annotation). The offset represents how many
  // steps to go left from the tail of the stream.
  const [offset, setOffset] = useState(0)
  const taskConfig = useTaskConfig()

  if (!samples || samples.length === 0 || !taskConfig) {
    return <span>Loading</span>
  }

  const currentSample = samples[samples.length - 1 - offset]
  const classPredictions = getSortedClassPredictions(currentSample, taskConfig)
  return (
    <div className="App">
      <div className="App__selector">
        <button
          onClick={() => setOffset(offset => offset + 1)}
          disabled={offset >= samples.length - 1}
        >
          Previous
        </button>
        <button
          onClick={() => setOffset(offset => offset - 1)}
          disabled={offset <= 0}
        >
          Next
        </button>
      </div>
      <div className="App__sample">
        {currentSample.text}
      </div>
      <ClassSelection
        className="App__annotation"
        classPredictions={classPredictions}
        label={currentSample.textClass || undefined}
        onChange={label => {
          const textClass = label || null
          updateSample(currentSample.id, textClass)
          if (offset === 0) {
            getNext()
          } else {
            setOffset(offset => offset - 1)
          }
        }}
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

  // Sort by value (confidence prediction) in descending order.
  return textClassPredictions.sort((a, b) => b.value - a.value)
}

export default App;
