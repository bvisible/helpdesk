<template>
  <div class="flex flex-col">
    <LayoutHeader>
      <template #left-header>
        <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
        <div class="text-lg-medium text-ink-gray-9">{{ __("Call Logs") }}</div>
      </template>
      <template #right-header>
        <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
        <Button
          :label="__('New Call Log')"
          theme="gray"
          variant="solid"
          @click="newCallLog"
          icon-left="lucide-plus"
        />
      </template>
    </LayoutHeader>
    <ListViewBuilder
      ref="listViewRef"
      :options="options"
      @row-click="openCallLog"
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
import Icon from "@/components/Icon.vue";
import LayoutHeader from "@/components/LayoutHeader.vue";
import ListViewBuilder from "@/components/ListViewBuilder.vue";
import { Avatar, Badge, Button, usePageMeta } from "frappe-ui";
import { computed, h, ref } from "vue";
import CallLogDetailModal from "./CallLogDetailModal.vue";
import CallLogModal from "./CallLogModal.vue";
import { statusColorMap, statusLabelMap } from "./utils";
import { PhoneIcon } from "@/components/icons";
//// Neoffice — added: __() import for the wraps below
import { __ } from "@/translation";

const showCallLogModal = ref(false);
const showCallLogDetailModal = ref(false);
const callLogId = ref("");

const listViewRef = ref(null);

//// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site
//// (statusLabelMap holds English labels, translated where shown, as CallArea.vue does)
const options = computed(() => {
  return {
    doctype: "TP Call Log",
    selectable: true,
    showSelectBanner: true,
    emptyState: {
      //// Neoffice — i18n of the v1.31.0 merge: __() wrap or label/value split (upstream shows this string in English on every non-English site)
      title: __("No Call Logs Found"),
      icon: PhoneIcon,
    },
    columnConfig: {
      caller: {
        prefix: ({ row }) => {
          return h(Avatar, {
            shape: "circle",
            image: row._caller?.image || "Unknown",
            //// Neoffice — i18n of the v1.31.0 merge: __() wrap or label/value split (upstream shows this string in English on every non-English site)
            label: row._caller?.label || __("Unknown"),
            size: "sm",
          });
        },
        custom: ({ row }) => {
          //// Neoffice — i18n of the v1.31.0 merge: __() wrap or label/value split (upstream shows this string in English on every non-English site)
          return h("span", row._caller?.label || __("Unknown"));
        },
      },
      receiver: {
        prefix: ({ row }) => {
          return h(Avatar, {
            shape: "circle",
            image: row._receiver?.image || "Unknown",
            //// Neoffice — i18n of the v1.31.0 merge: __() wrap or label/value split (upstream shows this string in English on every non-English site)
            label: row._receiver?.label || __("Unknown"),
            size: "sm",
          });
        },
        custom: ({ row }) => {
          //// Neoffice — i18n of the v1.31.0 merge: __() wrap or label/value split (upstream shows this string in English on every non-English site)
          return h("span", row._receiver?.label || __("Unknown"));
        },
      },
      type: {
        prefix: ({ row }) => {
          let icon =
            row.type === "Incoming"
              ? "lucide-phone-incoming"
              : "lucide-phone-outgoing";
          return h(Icon, {
            icon,
            class: ["size-3 shrink-0"],
          });
        },
      },
      status: {
        custom: ({ row }) => {
          return h(Badge, {
            //// Neoffice — i18n of the v1.31.0 merge: __() wrap or label/value split (upstream shows this string in English on every non-English site)
            label: __(statusLabelMap[row.status]),
            variant: "subtle",
            theme: statusColorMap[row.status],
          });
        },
      },
      duration: {
        prefix: () => {
          return h(Icon, {
            icon: "lucide-clock",
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

usePageMeta(() => {
  return {
    //// Neoffice — i18n of the v1.31.0 merge: __() wrap or label/value split (upstream shows this string in English on every non-English site)
    title: __("Call Logs"),
  };
});
</script>
