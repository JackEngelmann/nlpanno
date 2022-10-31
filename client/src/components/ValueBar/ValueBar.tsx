import { classNames } from "../../classNames";
import styles from "./ValueBar.module.css";

type Props = {
  className?: string;
  // Value between 0 and 1.
  value: number;
};

export function ValueBar(props: Props) {
  const { className, value } = props;
  const width = value * 100 + "%";
  return (
    <div className={classNames(styles.container, className)}>
      <div className={styles.bar} style={{ width }} />
    </div>
  );
}
