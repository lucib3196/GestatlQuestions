
import { MyButton } from "../Base/Button";

type ButtonActionsProps = {
  isSubmitted: boolean;
  showSolution: () => void;
  handleSubmit: () => void;
  generateVarient: () => void;
};
export function ButtonActions({
  isSubmitted,
  showSolution,
  handleSubmit,
  generateVarient,
}: ButtonActionsProps) {
  return (
    <div className="grid grid-cols-3 gap-10 mb-10">
      <MyButton
        name={"Generate Variation"}
        onClick={generateVarient}
        variant="secondary"
      />
      <MyButton name={"Show Solution"} variant="third" onClick={showSolution} />
      <MyButton
        name={"Submit"}
        btype="submit"
        onClick={handleSubmit}
        disabled={isSubmitted}
      />
    </div>
  );
}
