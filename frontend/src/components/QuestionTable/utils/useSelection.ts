import { useCallback, useMemo, useState } from "react";

type CheckedQuestion = {
  id: string; // The idx of the question
  title: string;
  isChecked: boolean;
};

export function useSelection() {
  const [map, setMap] = useState<Map<string, CheckedQuestion>>(new Map());

  const isSelected = useCallback((id: string) => map.has(id), [map]);
  const selected = useMemo(() => Array.from(map.values()), [map]);

  const toggle = useCallback(
    (id: string, title: string, isChecked: boolean) => {
      setMap((prev) => {
        const next = new Map(prev);
        if (isChecked) {
          next.set(id, { id, title, isChecked });
        } else next.delete(id);
        return next;
      });
    },
    []
  );
  const clear = useCallback(() => setMap(new Map()), []);

  return { isSelected, selected, toggle, clear, count: selected.length };
}
