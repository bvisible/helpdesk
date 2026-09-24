<template>
  <div class="flex flex-col">
    <LayoutHeader>
      <!-- //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
      <template #left-header>
        <div class="text-lg font-medium text-ink-gray-9">{{ __("Call Logs") }}</div>
      </template>
      <template #right-header>
        <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
        <Button
          :label="__('New Call Log')"
          theme="gray"
          variant="solid"
          @click="newCallLog"
          icon-left="plus"
        />
      </template>
    </LayoutHeader>
    <ListViewBuilder
      ref="listViewRef"
      :options="options"
      @row-click="openCallLog"
      @empty-state-action="showCallLogModal = true"
    />
    <CallLogDetailModal
      v-model="showCallLogDetailModal"
      v-model:callLogModal="showCallLogModal"
      :callLogId="callLogId"
    />
    <CallLogModal
      v-model="showCallLogModal"
      :callLogId="callLogId"
      @after-insert="
        () => {
          listViewRef?.reload();
        }
      "
    />
  </div>
</template>

<script setup lang="ts">
import LayoutHeader from "@/components/LayoutHeader.vue";
import ListViewBuilder from "@/components/ListViewBuilder.vue";
import { Avatar, Badge, Button, FeatherIcon, usePageMeta } from "frappe-ui";
import { computed, h, ref } from "vue";
import CallLogDetailModal from "./CallLogDetailModal.vue";
import CallLogModal from "./CallLogModal.vue";
//// Neoffice — statusLabel added: the status label translated when it is shown (utils.ts).
import { statusColorMap, statusLabel } from "./utils";
import { PhoneIcon } from "@/components/icons";
//// Neoffice — added: __() import for the i18n pass below (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
import { __ } from "@/translation";

const showCallLogModal = ref(false);
const showCallLogDetailModal = ref(false);
const callLogId = ref("");

const listViewRef = ref(null);

const options = computed(() => {
  return {
    doctype: "TP Call Log",
    selectable: true,
    showSelectBanner: true,
    //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
    emptyState: {
      title: __('No Call Logs Found'),
      icon: PhoneIcon,
    },
    columnConfig: {
      caller: {
        prefix: ({ row }) => {
          return h(Avatar, {
            shape: "circle",
            image: row._caller?.image || "Unknown",
            //// Neoffice — upstream wrote the fallback name in plain English; wrapped so the French
            //// catalogue reaches it (same pass as 71a5669d9). The `image` fallback is not text.
            label: row._caller?.label || __("Unknown"),
            size: "sm",
          });
        },
        custom: ({ row }) => {
          //// Neoffice — see above
          return h("span", row._caller?.label || __("Unknown"));
        },
      },
      receiver: {
        prefix: ({ row }) => {
          return h(Avatar, {
            shape: "circle",
            image: row._receiver?.image || "Unknown",
            //// Neoffice — see the caller column above
            label: row._receiver?.label || __("Unknown"),
            size: "sm",
          });
        },
        custom: ({ row }) => {
          //// Neoffice — see the caller column above
          return h("span", row._receiver?.label || __("Unknown"));
        },
      },
      type: {
        prefix: ({ row }) => {
          let icon =
            row.type === "Incoming" ? "phone-incoming" : "phone-outgoing";
          return h(FeatherIcon, {
            name: icon,
            class: ["size-3 shrink-0"],
          });
        },
      },
      status: {
        custom: ({ row }) => {
          return h(Badge, {
            //// Neoffice — statusLabel() translates the status when it is shown, and declares every
            //// label to the extractor (call-logs/utils.ts; same pass as 71a5669d9)
            label: statusLabel(row.status),
            variant: "subtle",
            theme: statusColorMap[row.status],
          });
        },
      },
      duration: {
        prefix: () => {
          return h(FeatherIcon, {
            name: "clock",
            class: ["size-3 shrink-0"],
          });
        },
        custom: ({ row }) => {
          return h("span", row.duration ? row.duration + "s" : "0s");
        },
      },
    },
  };
});

const newCallLog = () => {
  callLogId.value = "";
  showCallLogModal.value = true;
};

function openCallLog(id: string): void {
  callLogId.value = id;
  showCallLogDetailModal.value = true;
}

//// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
usePageMeta(() => {
  return {
    title: __('Call Logs'),
  };
});
</script>
