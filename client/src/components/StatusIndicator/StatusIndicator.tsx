import { classNames } from "../../classNames";
import styles from "./StatusIndicator.module.css";

type Props = {
    isWorking: boolean
}

export function StatusIndicator(props: Props) {
    const { isWorking } = props
    const className = classNames(styles.root, isWorking && styles.working)
    return <div className={className}><div className={styles.bar} /></div>
}
