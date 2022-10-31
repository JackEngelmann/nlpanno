import { ReactNode, useEffect, useMemo, useState } from "react";
import { classNames } from "../../classNames";
import styles from "./SearchableList.module.css";

type Props<Item> = {
  className?: string;
  doesMatch(item: Item, text: string): boolean;
  items: Item[];
  onChange(item: Item): void;
  placeholder?: string;
  renderItem(item: Item, isSelected: boolean, onChange: () => void): ReactNode;
};

export function SearchableList<Item>(props: Props<Item>) {
  const {
    items,
    doesMatch,
    onChange,
    className,
    renderItem,
    placeholder = "Search...",
  } = props;
  const [text, setText] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);

  const matchingItems = useMemo(() => {
    if (text.length <= 1) return items;
    return items.filter((i) => doesMatch(i, text));
  }, [items, text, doesMatch]);

  useEffect(() => {
    if (selectedIndex > matchingItems.length - 1) {
      setSelectedIndex(matchingItems.length - 1);
    }
    if (selectedIndex < 0) {
      setSelectedIndex(0);
    }
  }, [setSelectedIndex, selectedIndex, matchingItems]);

  function onKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter") {
      onChange(matchingItems[selectedIndex]);
      setText("");
    }
    if (event.key === "ArrowDown") {
      setSelectedIndex((index) =>
        Math.min(index + 1, matchingItems.length - 1)
      );
    }
    if (event.key === "ArrowUp") {
      setSelectedIndex((index) => Math.max(index - 1, 0));
    }
  }

  return (
    <div className={classNames(className, styles.root)}>
      <input
        className={styles.input}
        autoFocus
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder={placeholder}
      />
      <ul className={styles.list}>
        {matchingItems.map((i, idx) =>
          renderItem(i, idx === selectedIndex, () => {
            onChange(i);
            setSelectedIndex(0);
            setText("");
          })
        )}
      </ul>
    </div>
  );
}
