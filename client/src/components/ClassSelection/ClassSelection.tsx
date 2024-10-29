import { AvailableTextClass, TextClass } from "../../types";
import { Card } from "../Card/Card";
import { SearchableList } from "../SearchableList/SearchableList";
import { ValueBar } from "../ValueBar/ValueBar";

type Props = {
  className?: string;
  availableTextClasses: AvailableTextClass[];
  label: TextClass | undefined;
  onChange(label: TextClass): void;
};

export function ClassSelection(props: Props) {
  function onChange(availableTextClass: AvailableTextClass) {
    props.onChange({
      id: availableTextClass.id,
      name: availableTextClass.name,
    })
  }
  return (
    <SearchableList
      className={props.className}
      items={props.availableTextClasses}
      onChange={onChange}
      renderItem={(c, isSelected, onClick) => (
        <Card key={c.id} onClick={onClick} isSelected={isSelected}>
          {c.name === props.label?.name ? <b>{c.name}</b> : c.name}
          <ValueBar value={c.confidence} />
        </Card>
      )}
      doesMatch={(c, text) =>
        c.name.toLowerCase().includes(text.toLowerCase())
      }
    />
  );
}
