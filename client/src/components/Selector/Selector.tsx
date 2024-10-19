import styles from "./Selector.module.css"

type Props = {
    onPrevious: () => void,
    onNext: () => void,
    isFirst: boolean,
    isLast: boolean,
    current: number,
    total: number,
}

export function Selector(props: Props) {
    return (
        <div className={styles.selector}>
            <button onClick={props.onPrevious} disabled={props.isFirst}>
                {"<"}
            </button>
            <span>{props.current + 1} / {props.total}</span>
            <button onClick={props.onNext} disabled={props.isLast}>
                {">"}
            </button>
        </div>
    )
}