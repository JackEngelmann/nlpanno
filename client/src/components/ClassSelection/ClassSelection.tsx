import { Card } from "../Card/Card";
import { SearchableList } from "../SearchableList/SearchableList";
import { ValueBar } from "../ValueBar/ValueBar";

type Props = {
  className?: string;
  classPredictions: {className: string, value: number}[];
  label: string | undefined;
  onChange(label: string | undefined): void;
};

export function ClassSelection(props: Props) {
  return (
    <SearchableList
      className={props.className}
      items={props.classPredictions}
      onChange={(classPrediction) => props.onChange(classPrediction.className)}
      renderItem={(c, isSelected, onClick) => (
        <Card key={c.className} onClick={onClick} isSelected={isSelected}>
          {c.className === props.label ? <b>{c.className}</b> : c.className}
          <ValueBar value={c.value} />
        </Card>
      )}
      doesMatch={(c, text) =>
        c.className.toLowerCase().includes(text.toLowerCase())
      }
    />
  );
}
