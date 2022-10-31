import { HTMLProps } from "react";
import { classNames } from "../../classNames";
import styles from "./Card.module.css";

type Props = HTMLProps<HTMLLIElement> & {
  isSelected?: boolean;
  noHover?: boolean;
};

export function Card(props: Props) {
  const { noHover, children, className, isSelected, ...restProps } = props;
  return (
    <li
      className={classNames(
        styles.root,
        className,
        isSelected ? styles.selected : undefined,
        restProps.onClick ? styles.clickable : undefined,
        noHover ? undefined : styles.hover
      )}
      {...restProps}
    >
      {props.children}
    </li>
  );
}
