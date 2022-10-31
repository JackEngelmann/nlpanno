import './App.css';
import { useSampleStream, useTaskConfig } from './api';
import { ClassSelection } from './components/ClassSelection/ClassSelection';
import { useState } from 'react';

function App() {
  const [samples, getNext, updateSample] = useSampleStream()
  const [offset, setOffset] = useState(0)
  const taskConfig = useTaskConfig()
  console.log(samples)
  console.log(offset)

  if (!samples || samples.length === 0 || !taskConfig) {
    return <span>Loading</span>
  }

  const currentSample = samples[samples.length - 1 - offset]
  let classPredictions: {className: string, value: number}[] = []
  const textClassPredictions = currentSample.textClassPredictions
  if (textClassPredictions) {
    classPredictions = taskConfig.textClasses.map((className, classIndex) => ({
      className,
      value: textClassPredictions[classIndex]
    })).sort((a, b) => b.value - a.value)
  } else {
    classPredictions = taskConfig.textClasses.map(n => ({ className: n, value: 0}))
  }
  return (
    <div className="App">
      <div>
        <button onClick={() => setOffset(offset => offset + 1)} disabled={offset >= samples.length - 1}>
          Previous
        </button>
        <button onClick={() => setOffset(offset => offset - 1)} disabled={offset <= 0}>
          Next
        </button>
      </div>
      {currentSample.text}
      <ClassSelection
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

export default App;
