//// Neoffice — added: the translate helper for statusLabel() below.
import { __ } from "@/translation";

export const statusColorMap = {
  Completed: "green",
  Busy: "orange",
  Failed: "red",
  Initiated: "gray",
  Queued: "gray",
  Canceled: "gray",
  Ringing: "gray",
  "No Answer": "red",
  "In Progress": "blue",
};

export const statusLabelMap = {
  Completed: "Completed",
  Initiated: "Initiated",
  Busy: "Declined",
  Failed: "Failed",
  Queued: "Queued",
  Canceled: "Canceled",
  Ringing: "Ringing",
  "No Answer": "Missed Call",
  "In Progress": "In Progress",
};

//// Neoffice — added: the call status as shown, translated when it is read. statusLabelMap above is
//// built at import, before the catalogue arrives, and "Declined" / "Missed Call" appear nowhere as a
//// literal __() call, so the extractor never put them in the catalogue: they showed in English.
export function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    Completed: __("Completed"),
    Initiated: __("Initiated"),
    Busy: __("Declined"),
    Failed: __("Failed"),
    Queued: __("Queued"),
    Canceled: __("Canceled"),
    Ringing: __("Ringing"),
    "No Answer": __("Missed Call"),
    "In Progress": __("In Progress"),
  };
  return labels[status] || status;
}
