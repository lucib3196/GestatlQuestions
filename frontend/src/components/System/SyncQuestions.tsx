import { FaSyncAlt } from "react-icons/fa";
import { PopUpHelpIcon } from "../Base/PopUpHelper";
import { toast } from "react-toastify";
import { questionApi } from "../../api";

export default function SyncQuestions() {
    const syncQuestions = async () => {
        try {
            const syncedMetrics = await questionApi.SyncQuestions();
            // Not sure there is a weird bug where it says deleted but i dont have any deleted
            const prunedQuestions = await questionApi.PruneQuestions();
            const deletedQuestions = prunedQuestions.metrics.deleted_from_db

            // Format metrics neatly for toast display
            const metricLines = Object.entries(syncedMetrics.metrics)
                .map(([key, value]) => `• ${key}: ${value}`)
                .join("\n");

            const results = [
                "✅ Sync Complete",
                "",
                "📊 Metrics:",
                metricLines,
                "",
                `🗑️ Deleted Questions: ${deletedQuestions}`,
            ].join("\n");

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
    }
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
