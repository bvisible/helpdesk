<template>
  <Tabs
    :modelValue="activeTab"
    @update:modelValue="changeTabTo"
    class="flex flex-1 flex-col overflow-hidden"
  >
    <!-- the row carries the underline so it runs beneath the actions too -->
    <div
      class="flex shrink-0 items-center gap-2 border-b border-outline-gray-1 px-5"
    >
      <TabList size="md" class="flex-1 !border-b-0 py-1.5">
        <TabTrigger
          v-for="tab in tabs"
          :key="tab.value"
          :value="tab.value"
          :label="tab.label"
          :icon-left="tab.iconLeft"
        />
      </TabList>
      <TicketCallActions v-if="activeTab === 'call'" />
    </div>
    <TabPanel
      v-for="tab in tabs"
      :key="tab.value"
      :value="tab.value"
      class="min-h-0 flex-1 flex-col overflow-auto data-[state=active]:flex"
    >
      <TicketAnalyticsTab v-if="tab.value === 'analytics'" />
      <TicketTimeline
        v-else
        :ticket-id="String(ticket.doc?.name)"
        :tab="tab.value"
        :tab-label="tab.label"
        @email:reply="(e) => communicationAreaRef?.replyToEmail(e)"
      />
    </TabPanel>
  </Tabs>
  <!-- Comm Area -->
  <CommunicationArea
    ref="communicationAreaRef"
    :ticketId="String(ticket.doc?.name)"
    :to-emails="[ticket.doc?.raised_by]"
    :cc-emails="[]"
    :bcc-emails="[]"
    :key="ticket.doc?.name"
    @update="reloadTicketFeed(String(ticket.doc?.name))"
  />
</template>

<script setup lang="ts">
import CommunicationArea from "@/components/CommunicationArea.vue";
import {
  ActivityIcon,
  CommentIcon,
  EmailIcon,
  PhoneIcon,
} from "@/components/icons";
import TicketAnalyticsTab from "@/components/ticket-agent/analytics/TicketAnalyticsTab.vue";
import TicketCallActions from "@/components/ticket/TicketCallActions.vue";
import { useActiveTabManager } from "@/composables/useActiveTabManager";
import { reloadTicketFeed } from "@/composables/useTicket";
import { useTelephonyStore } from "@/stores/telephony";
import { TabObject, TicketSymbol } from "@/types";
import { TabList, TabPanel, TabTrigger, Tabs } from "frappe-ui";
import { storeToRefs } from "pinia";
//// Neoffice — added: __() import for the wraps below
import { __ } from "@/translation";
import { computed, ComputedRef, inject, ref } from "vue";
import LucideChartNoAxesColumn from "~icons/lucide/chart-no-axes-column";
import TicketTimeline from "./timeline/TicketTimeline.vue";

const ticket = inject(TicketSymbol)!;

const communicationAreaRef = ref<InstanceType<typeof CommunicationArea> | null>(
  null
);
const telephonyStore = useTelephonyStore();
const { isCallingEnabled } = storeToRefs(telephonyStore);

//// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site (label only, the value is the URL hash)
const tabs: ComputedRef<TabObject[]> = computed(() => {
  const _tabs: TabObject[] = [
    {
      value: "activity",
      //// Neoffice — i18n of the v1.31.0 merge: __() wrap or label/value split (upstream shows this string in English on every non-English site)
      label: __("Activity"),
      iconLeft: ActivityIcon,
    },
    {
      value: "email",
      //// Neoffice — i18n of the v1.31.0 merge: __() wrap or label/value split (upstream shows this string in English on every non-English site)
      label: __("Emails"),
      iconLeft: EmailIcon,
    },
    {
      value: "comment",
      //// Neoffice — i18n of the v1.31.0 merge: __() wrap or label/value split (upstream shows this string in English on every non-English site)
      label: __("Comments"),
      iconLeft: CommentIcon,
    },
  ];

  if (isCallingEnabled.value) {
    _tabs.push({
      value: "call",
      //// Neoffice — i18n of the v1.31.0 merge: __() wrap or label/value split (upstream shows this string in English on every non-English site)
      label: __("Calls"),
      iconLeft: PhoneIcon,
    });
  }
  _tabs.push({
    value: "analytics",
    //// Neoffice — i18n of the v1.31.0 merge: __() wrap or label/value split (upstream shows this string in English on every non-English site)
    label: __("Analytics"),
    iconLeft: LucideChartNoAxesColumn,
  });
  return _tabs;
});

const { activeTab, changeTabTo } = useActiveTabManager(tabs);
</script>
