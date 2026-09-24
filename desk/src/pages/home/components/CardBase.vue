<template>
  <div class="flex flex-col w-full h-full rounded-md p-4">
    <slot name="title">
      <div class="text-ink-gray-5 text-base mb-2">
        {{ title }}
      </div>
    </slot>
    <div class="flex flex-col gap-2 h-full w-full">
      <div class="flex items-end w-full gap-2">
        <div
          class="text-2xl font-medium text-center text-ink-gray-8 whitespace-nowrap"
        >
          {{ text }}
        </div>
        <div class="flex items-center text-sm gap-1">
          <div class="flex items-center gap-1" :class="percentageChange.color">
            <FeatherIcon :name="percentageChange.icon" class="size-4" />
            <div>{{ percentageChange.value }}%</div>
          </div>
          <Dropdown :options="durationOptions">
            <div
              class="flex items-center gap-0.5 text-ink-gray-5 hover:text-ink-gray-6 cursor-pointer shrink-0"
            >
              <!-- //// Neoffice — "vs" wrapped, and the period translated here, at display: currentDuration is the English key ("Last month"...) that the cards send as `period` (see durationOptions) -->
              <div class="rtl:flex rtl:gap-1">
                <span>{{ __("vs") }}</span> <span>{{ __(currentDuration).toLowerCase() }}</span>
              </div>
              <FeatherIcon name="chevron-down" class="size-4" />
            </div>
            <template #item-label="{ item }">
              <div
                class="data-[disabled]:cursor-not-allowed group flex w-full items-center rounded px-2 text-base focus:outline-none focus:bg-surface-gray-3 data-[highlighted]:bg-surface-gray-3 data-[state=open]:bg-surface-gray-3 whitespace-nowrap text-ink-gray-7 cursor-pointer justify-between"
              >
                <span>
                  {{ item.label }}
                </span>
              </div>
            </template>
            <template #item-suffix="{ item }">
              <FeatherIcon
                v-if="item.label == __(currentDuration)"
                name="check"
                class="size-4"
              />
            </template>
          </Dropdown>
        </div>
      </div>
      <slot name="chart">
        <div v-if="chartConfig" class="w-full h-full">
          <ECharts :options="chartConfig" class="w-full h-full" />
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, type PropType } from "vue";
import { Dropdown, FeatherIcon, ECharts } from "frappe-ui";
import { __ } from "@/translation";
import { EChartsOption } from "echarts";
import { DropdownOption } from "@/types";

const props = defineProps({
  title: {
    type: String,
  },
  text: {
    type: [Number, String] as PropType<number | string>,
    default: "",
  },
  percentageChange: {
    type: Object,
    required: true,
  },
  chartConfig: {
    type: Object as PropType<EChartsOption>,
    required: true,
  },
  currentDuration: {
    type: String,
    //// Neoffice — the English key, not its translation: a prop default is evaluated with the
    //// component definition (before the catalogue arrives), and the value is an identity (below).
    default: "Last month",
  },
});

const chartConfig = computed<EChartsOption>(() => props.chartConfig);

const currentDuration = computed(() => props.currentDuration);

const emit = defineEmits(["changeDuration"]);

//// Neoffice — value / label split. Upstream emitted the TRANSLATED label, and the cards send it
//// lowercased as `period` to agent_home._resolve_window(), which only knows "last week",
//// "last month" and "last 3 months" and falls back to 30 days: on a French site "Semaine
//// dernière" and "3 derniers mois" both showed last month's figures. The English key travels,
//// the label is translated (the template's check mark compares __(currentDuration) with it).
const durationOptions = [
  {
    label: __("Last week"),
    onClick: () => {
      //// Neoffice — English key (see the note above durationOptions)
      if (currentDuration.value == "Last week") return;
      emit("changeDuration", "Last week");
    },
  },
  {
    label: __("Last month"),
    onClick: () => {
      //// Neoffice — English key (see the note above durationOptions)
      if (currentDuration.value == "Last month") return;
      emit("changeDuration", "Last month");
    },
  },
  {
    label: __("Last 3 months"),
    onClick: () => {
      //// Neoffice — English key (see the note above durationOptions)
      if (currentDuration.value == "Last 3 months") return;
      emit("changeDuration", "Last 3 months");
    },
  },
];
</script>
