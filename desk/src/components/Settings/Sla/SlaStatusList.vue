<template>
  <div class="flex gap-5 w-full">
    <!-- //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
    <FormControl
      type="autocomplete"
      :label="__('Default ticket status')"
      :options="openStatuses"
      class="flex-1"
      v-model="slaData.default_ticket_status"
    />
    <!-- //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
    <FormControl
      type="autocomplete"
      :label="__('Ticket reopen status')"
      :options="openStatuses"
      class="flex-1"
      v-model="slaData.reopen_ticket_status"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ComputedRef } from "vue";
import { slaData } from "@/stores/sla";
import { useTicketStatusStore } from "@/stores/ticketStatus";
import { HDTicketStatus } from "@/types/doctypes";
//// Neoffice — ticket-status translation: the statuses below are displayed through
//// statusLabel() (stores/ticketStatus.ts). __ came with it; the template's __() calls bind to
//// it, the same function as the global __.
import { __ } from "@/translation";

const { statuses, statusLabel } = useTicketStatusStore();

const openStatuses: ComputedRef<HDTicketStatus[]> = computed(() => {
  return (
    statuses?.data
      ?.filter((s: HDTicketStatus) => s.category === "Open")
      ?.map((s: HDTicketStatus) => {
        return {
          //// Neoffice — the STATUS LABEL is displayed, so it goes through __(); the
          //// VALUE stays raw because it is what HD Ticket.status stores and what the
          //// filters send back. A default label ('Open', 'Replied') is in the merged
          //// catalogue and turns French; a label an instance renamed is absent from it
          //// and __() returns it unchanged, which is right — it is already in their
          //// words. Upstream already does this in ShareFeedback.vue and nowhere else.
          label: statusLabel(s.label_agent),
          value: s.label_agent,
        };
      }) || []
  );
});
</script>
