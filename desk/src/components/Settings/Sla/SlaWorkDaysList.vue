<template>
  <div class="rounded-md border px-2 border-outline-gray-2 text-sm">
    <div
      class="grid p-2 px-4 items-center"
      :style="{
        gridTemplateColumns: getGridTemplateColumnsForTable(columns),
      }"
      v-if="slaData.support_and_resolution?.length !== 0"
    >
      <div
        v-for="column in columns"
        :key="column.key"
        class="text-ink-gray-5 overflow-hidden whitespace-nowrap text-ellipsis"
        :class="{
          'ms-2': column.key === 'workday',
        }"
      >
        {{ column.label }}
        <span v-if="column.isRequired" class="text-ink-red-3">*</span>
      </div>
    </div>
    <hr v-if="slaData.support_and_resolution?.length !== 0" />
    <SlaWorkDaysListItem
      v-for="(row, index) in slaData.support_and_resolution"
      :key="index + row.workday + row.id"
      :row="row"
      :columns="columns"
      :isLast="index === slaData.support_and_resolution.length - 1"
    />
    <div
      v-if="slaData.support_and_resolution?.length === 0"
      class="text-center p-4 text-ink-gray-5"
    >
      <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
      {{ __("No workdays in the list") }}
    </div>
  </div>
  <div class="flex items-center justify-between mt-2.5">
    <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
    <Button
      v-if="slaData.support_and_resolution.length < 7"
      variant="subtle"
      :label="__('Add row')"
      @click="addWorkDay"
      icon-left="plus"
    />
    <ErrorMessage :message="slaDataErrors.support_and_resolution" />
  </div>
</template>

<script setup lang="ts">
import { Button } from "frappe-ui";
import SlaWorkDaysListItem from "./SlaWorkDaysListItem.vue";
import { slaData, slaDataErrors } from "@/stores/sla";
import { getGridTemplateColumnsForTable } from "@/utils";
//// Neoffice — added import: __() used by the i18n wraps in this file (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
import { __ } from "@/translation";

interface Column {
  key: string;
  label: string;
  isRequired?: boolean;
}

const allDays = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];

const addWorkDay = () => {
  const usedDays = new Set(
    slaData.value.support_and_resolution.map((day) => day.workday)
  );
  const nextDay = allDays.find((day) => !usedDays.has(day)) || allDays[0];

  slaData.value.support_and_resolution.push({
    workday: nextDay,
    start_time: "09:00:00",
    end_time: "17:00:00",
    id: Math.random().toString(36).substring(2, 9),
  });
};

const columns: Column[] = [
  {
    //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
    label: __('Day'),
    key: "workday",
    isRequired: true,
  },
  {
    //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
    label: __('Start time'),
    key: "start_time",
    isRequired: true,
  },
  {
    //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
    label: __('End time'),
    key: "end_time",
    isRequired: true,
  },
];
</script>
