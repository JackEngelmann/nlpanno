import styles from "./LoadingScreen.module.css"

export function LoadingScreen() {
  return (
    <div className={styles.root}>
      <div className={styles.loading}>Loading...</div>
    </div>
  )
}