import { FaSyncAlt } from "react-icons/fa";
import { PopUpHelpIcon } from "../Base/PopUpHelper";
import { toast } from "react-toastify";
import { QuestionSyncAPI } from "../../api/questionSync";
import type { FolderCheckMetrics, SyncMetrics } from "../../types/syncTypes";

function FormatMetrics(metrics: SyncMetrics, deleted: FolderCheckMetrics) {
  const metricLines = Object.entries(metrics)
    .map(([key, value]) => `• ${key}: ${value}`)
    .join("\n");

  const results = [
    "✅ Sync Complete",
    "📊 Metrics:",
    metricLines,
    `🗑️ Deleted Questions: ${deleted.deleted_from_db}`,
  ].join("\n");
  return results;
}

export default function SyncQuestions() {
  const syncQuestions = async () => {
    try {
      const syncedMetrics = await QuestionSyncAPI.SyncQuestions();
      // Not sure there is a weird bug where it says deleted but i dont have any deleted
      const prunedQuestions = await QuestionSyncAPI.PruneMissingQuestions();

      const results = FormatMetrics(syncedMetrics, prunedQuestions);

      toast.info(results, {
        position: "top-right",
        style: { whiteSpace: "pre-line" }, // preserves line breaks
      });
    } catch (error) {
      toast.error(`Sync Failed\n${String(error)}`, {
        position: "top-right",
        autoClose: 4000,
      });
    }
  };
  return (
    <div className=" relative flex flex-col items-center ">
      <PopUpHelpIcon
        onClick={syncQuestions}
        value="Syncs local questions and removes deleted ones."
        icon={FaSyncAlt}
      />
    </div>
  );
}
