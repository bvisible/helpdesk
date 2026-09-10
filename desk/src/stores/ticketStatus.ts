import { HDTicketStatus } from "@/types/doctypes";
import { parseColor } from "@/utils";
import { createListResource } from "frappe-ui";
import { defineStore } from "pinia";
import { __ } from "@/translation";

export const useTicketStatusStore = defineStore("ticketStatus", () => {
  const statuses = createListResource({
    doctype: "HD Ticket Status",
    cache: ["HD Ticket Status", "list"],
    fields: [
      "label_agent",
      "label_customer",
      "order",
      "different_view",
      "category",
      "color",
      "enabled",
    ],
    orderBy: "`tabHD Ticket Status`.order",
    pageLength: 1000,
    auto: true,
    transform: (data: HDTicketStatus[]) => {
      return data.map((d) => {
        if (!d.different_view) {
          d.label_customer = d.label_agent;
        }
        d["parsed_color"] = parseColor(d.color);
        return d;
      });
    },
  });

  //// Neoffice — a ticket STATUS must not be translated through the bare msgid
  //// "Open". Measured on the dev instance: 14 installed apps translate that msgid,
  //// 9 as "Ouvert" (the state) and 5 as "Ouvrir" (the verb) — and
  //// get_translations_from_apps merges them in installed-apps order, so the LAST
  //// app installed decides for the whole site. On this instance `letters` won and
  //// the ticket list read "Ouvrir", which is not a state, it is an instruction.
  //// Worse, it varies from instance to instance with the install order.
  ////
  //// So the four default labels get msgid of their own, qualified with their
  //// domain, that no other app can overwrite. Any other label is a name the
  //// instance chose: returned as-is, because it is already in their words.
  //// The msgid are written as LITERAL __() calls, not as strings looked up
  //// through a variable: `bench generate-pot-file` extracts literals only, so a
  //// first version that stored "Ticket status: Open" as an object VALUE never
  //// reached the POT — and the next `update-po-files` then deleted the entries I
  //// had added by hand, as obsolete. The screen printed the raw msgid.
  //// Functions, not strings, so each call is evaluated when the label is shown
  //// and picks up the reader's language.
  const DEFAULT_STATUS_LABELS: Record<string, () => string> = {
    Open: () => __("Ticket status: Open"),
    Replied: () => __("Ticket status: Replied"),
    Paused: () => __("Ticket status: Paused"),
    Resolved: () => __("Ticket status: Resolved"),
    Closed: () => __("Ticket status: Closed"),
  };

  function statusLabel(label: string | undefined): string {
    if (!label) return "";
    const translate = DEFAULT_STATUS_LABELS[label];
    return translate ? translate() : label;
  }

  function getStatus(label: string): HDTicketStatus | undefined {
    return statuses.data?.find(
      (s: HDTicketStatus) =>
        s.label_agent === label || s.label_customer === label
    );
  }
  const colorMap = {
    Green: ["text-green-700", "bg-surface-green-2"],
    Black: ["text-black", "bg-surface-gray-2"],
    Gray: ["text-gray-700", "bg-surface-gray-2"],
    Blue: ["text-blue-700", "bg-surface-blue-2"],
    Red: ["text-red-500", "bg-surface-red-1"],
    Pink: ["text-pink-500", "bg-surface-pink-1"],
    Orange: ["text-orange-600", "bg-surface-orange-1"],
    Amber: ["text-amber-700", "bg-surface-amber-2"],
    Yellow: ["text-yellow-700", "bg-surface-amber-2"],
    Cyan: ["text-cyan-700", "bg-surface-cyan-1"],
    Teal: ["text-teal-700", "bg-teal-100"],
    Violet: ["text-violet-700", "bg-surface-violet-1"],
    Purple: ["text-purple-700", "bg-purple-100"],
    Default: ["text-ink-gray-9", "bg-surface-gray-2"],
  };

  return {
    statuses,
    colorMap,
    getStatus,
    statusLabel,
  };
});
function parseColor(color: string): string {
  color = color.toLowerCase();
  let textColor = `!text-${color}-600`;
  if (color == "black") {
    textColor = "!text-ink-gray-9";
  } else if (["gray", "green"].includes(color)) {
    textColor = `!text-${color}-700`;
  }

  return textColor;
}
