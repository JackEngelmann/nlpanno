import { Link } from "react-router-dom"
import { useTasks } from "../api"
import { ErrorScreen } from "../components/ErrorScreen/ErrorScreen"
import { LoadingScreen } from "../components/LoadingScreen/LoadingScreen"
import { AnnotationTask } from "../types"

export function TasksScreen() {
  const { data: tasks, isLoading, errorOccurred } = useTasks()
  if (isLoading) return <LoadingScreen />
  if (errorOccurred) return <ErrorScreen />
  function renderTask(task: AnnotationTask) {
    return (
      <li key={task.id}>
        <Link to={`/tasks/${task.id}`}>{task.name}</Link>
      </li>
    )
  }
  return <ul>{tasks!.map(renderTask)}</ul>
}
