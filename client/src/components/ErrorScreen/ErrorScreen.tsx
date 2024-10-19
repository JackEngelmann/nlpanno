import styles from "./ErrorScreen.module.css"

export function ErrorScreen() {
  return (
    <div className={styles.root}>
      <div className={styles.error}>{"An Error occurred :("}</div>
    </div>
  )
}
