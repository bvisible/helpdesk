<template>
  <div class="rounded-md border p-1 border-outline-gray-2 text-sm">
    <div
      class="grid p-2 items-center"
      :style="{
        gridTemplateColumns: '1fr 4fr 22px',
      }"
      v-if="holidays?.length !== 0"
    >
      <div
        v-for="column in columns"
        :key="column.key"
        class="text-ink-gray-5 overflow-hidden whitespace-nowrap text-ellipsis"
      >
        {{ column.label }}
      </div>
    </div>
    <hr class="my-0.5" v-if="holidays?.length !== 0" />
    <div v-for="(holiday, index) in holidays" :key="holiday.day">
      <div
        class="grid gap-2 px-2 py-2 items-center"
        :style="{ gridTemplateColumns: '1fr 4fr 22px' }"
      >
        <div
          v-for="column in columns"
          :key="column.key"
          class="w-full py-2 overflow-hidden whitespace-nowrap text-ellipsis"
        >
          <div v-if="column.key === 'repetition'">
            {{ getRepetitionText(holiday[column.key]) }}
          </div>
          <div v-else>{{ holiday[column.key] }}</div>
        </div>
        <div class="flex justify-end">
          <Dropdown placement="right" :options="dropdownOptions(holiday)">
            <Button
              icon="more-horizontal"
              variant="ghost"
              @click="isConfirmingDelete = false"
            />
          </Dropdown>
        </div>
      </div>
      <hr class="my-0.5" v-if="index !== holidays.length - 1" />
    </div>
    <!-- //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
    <div v-if="holidays?.length === 0" class="text-center p-4 text-ink-gray-5">
      {{ __("No items in the list") }}
    </div>
  </div>
  <!-- //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
  <Button
    variant="subtle"
    @click="addHoliday"
    class="mt-2.5"
    :label="__('Add Recurring Holiday')"
    icon-left="plus"
  />
  <!-- //// Neoffice — the dialog titles were plain English; wrapped so the French catalogue reaches them (same pass as 71a5669d9) -->
  <Dialog
    v-model="dialog"
    :options="{
      size: 'md',
      title: recurringHolidayData.isEditing
        ? __('Edit Recurring Holiday')
        : __('Add Recurring Holiday'),
    }"
  >
    <template #body-content>
      <!-- //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
      <div v-if="!props.holidayData.from_date || !props.holidayData.to_date">
        <div class="text-center p-4 text-ink-gray-5">
          {{ __("Please select start and end date first") }}
        </div>
      </div>
      <div v-else class="flex flex-col gap-4">
        <div class="flex flex-col gap-1.5">
          <!-- //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
          <FormLabel :label="__('Day')" required />
          <Select
            :options="availableWorkDays"
            v-model="recurringHolidayData.day"
            :disabled="availableWorkDays.length === 0"
          />
        </div>
        <div class="flex flex-col gap-1.5">
          <!-- //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
          <FormLabel :label="__('Repetition')" required />
          <div class="grid grid-cols-2 gap-2 mt-2">
            <!-- //// Neoffice ▼▼▼ — wrapped in __() so the French catalogue can translate these repetition checkboxes; upstream showed them in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
            <Checkbox
              v-model="recurringHolidayData.repetition.all"
              :label="__('Every week')"
              :disabled="
                recurringHolidayData.repetition.first ||
                recurringHolidayData.repetition.second ||
                recurringHolidayData.repetition.third ||
                recurringHolidayData.repetition.fourth
              "
            />
            <!-- //// Neoffice — see the block marker above: __() i18n wrap -->
            <Checkbox
              v-model="recurringHolidayData.repetition.first"
              :label="__('Every first week')"
              :disabled="recurringHolidayData.repetition.all"
            />
            <!-- //// Neoffice — see the block marker above: __() i18n wrap -->
            <Checkbox
              v-model="recurringHolidayData.repetition.second"
              :label="__('Every second week')"
              :disabled="recurringHolidayData.repetition.all"
            />
            <!-- //// Neoffice — see the block marker above: __() i18n wrap -->
            <Checkbox
              v-model="recurringHolidayData.repetition.third"
              :label="__('Every third week')"
              :disabled="recurringHolidayData.repetition.all"
            />
            <!-- //// Neoffice — see the block marker above: __() i18n wrap -->
            <Checkbox
              v-model="recurringHolidayData.repetition.fourth"
              :label="__('Every fourth week')"
              :disabled="recurringHolidayData.repetition.all"
            />
            <!-- //// Neoffice — see the block marker above: __() i18n wrap -->
            <Checkbox
              v-model="recurringHolidayData.repetition.fifth"
              :label="__('Every fifth week')"
              :disabled="recurringHolidayData.repetition.all"
            />
            <!-- //// Neoffice ▲▲▲ -->
          </div>
        </div>
      </div>
    </template>
    <template #actions>
      <!-- //// Neoffice — the button labels were plain English; wrapped so the French catalogue reaches them (same pass as 71a5669d9) -->
      <Button
        variant="solid"
        @click="saveHoliday"
        class="w-full"
        v-if="props.holidayData.from_date && props.holidayData.to_date"
        :label="
          recurringHolidayData.isEditing ? __('Update Holiday') : __('Add Holiday')
        "
        :icon-left="recurringHolidayData.isEditing ? 'edit-2' : 'plus'"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { updateWeeklyOffDates } from "@/stores/holidayList";
import { ConfirmDelete } from "@/utils";
import dayjs from "dayjs";
import isSameOrBefore from "dayjs/plugin/isSameOrBefore";
import weekday from "dayjs/plugin/weekday";
import { Checkbox, Dropdown, FormLabel, Select, toast } from "frappe-ui";
import { computed, ref } from "vue";
import { getRepetitionText } from "./utils";
//// Neoffice — added: __() import for the i18n pass below (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
import { __ } from "@/translation";

dayjs.extend(weekday);
dayjs.extend(isSameOrBefore);

const dialog = ref(false);
const recurringHolidayData = ref({
  day: null,
  repetition: {
    all: false,
    first: false,
    second: false,
    third: false,
    fourth: false,
    fifth: false,
  },
  isEditing: false,
  editIndex: -1,
});

const props = defineProps({
  holidays: {
    type: Array<any>,
    default: () => [],
    required: true,
  },
  holidayData: {
    type: Object,
    default: () => {},
    required: true,
  },
});

//// Neoffice — wrapped in __() so the French catalogue can translate these column labels; upstream showed them in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
const columns = [
  {
    label: __('Day'),
    key: "day",
  },
  {
    //// Neoffice — see the block marker above: __() i18n wrap
    label: __('Repetition'),
    key: "repetition",
  },
];

//// Neoffice ▼▼▼ — wrapped in __() so the French catalogue can translate these weekday labels; upstream showed them in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
const workDays = ref([
  {
    label: __('Monday'),
    value: "Monday",
  },
  {
    //// Neoffice — see the block marker above: __() i18n wrap
    label: __('Tuesday'),
    value: "Tuesday",
  },
  {
    //// Neoffice — see the block marker above: __() i18n wrap
    label: __('Wednesday'),
    value: "Wednesday",
  },
  {
    //// Neoffice — see the block marker above: __() i18n wrap
    label: __('Thursday'),
    value: "Thursday",
  },
  {
    //// Neoffice — see the block marker above: __() i18n wrap
    label: __('Friday'),
    value: "Friday",
  },
  {
    //// Neoffice — see the block marker above: __() i18n wrap
    label: __('Saturday'),
    value: "Saturday",
  },
  {
    //// Neoffice — see the block marker above: __() i18n wrap
    label: __('Sunday'),
    value: "Sunday",
  },
]);
//// Neoffice ▲▲▲

//// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
const dropdownOptions = (holiday: any) => [
  {
    label: __('Edit'),
    onClick: () => editHoliday(holiday),
    icon: "edit",
  },
  ...ConfirmDelete({
    onConfirmDelete: () => deleteHoliday(holiday),
    isConfirmingDelete,
  }),
];

const availableWorkDays = computed(() => {
  const usedDays = new Set(
    props.holidays
      .filter(
        (_, index) =>
          !recurringHolidayData.value.isEditing ||
          index !== recurringHolidayData.value.editIndex
      )
      .map((h) => h.day)
  );

  if (recurringHolidayData.value.isEditing && recurringHolidayData.value.day) {
    usedDays.delete(recurringHolidayData.value.day);
  }

  return workDays.value.filter((day) => !usedDays.has(day.value));
});

const isConfirmingDelete = ref(false);

const addHoliday = () => {
  recurringHolidayData.value = {
    day: null,
    repetition: {
      all: false,
      first: false,
      second: false,
      third: false,
      fourth: false,
      fifth: false,
    },
    isEditing: false,
    editIndex: -1,
  };
  dialog.value = true;
};

const editHoliday = (holiday: any) => {
  const index = props.holidays.findIndex((h) => h.day === holiday.day);
  recurringHolidayData.value = {
    ...JSON.parse(JSON.stringify(holiday)),
    isEditing: true,
    editIndex: index,
  };
  dialog.value = true;
};

const saveHoliday = () => {
  if (!recurringHolidayData.value.day) {
    //// Neoffice — upstream wrote it in plain English; wrapped so the French catalogue reaches it (same pass as 71a5669d9)
    toast.error(__("Please select a day of the week"));
    return;
  }

  const { all, first, second, third, fourth, fifth } =
    recurringHolidayData.value.repetition;
  if (!all && !first && !second && !third && !fourth && !fifth) {
    //// Neoffice — upstream wrote it in plain English; wrapped so the French catalogue reaches it (same pass as 71a5669d9)
    toast.error(__("Please select at least one repetition option"));
    return;
  }

  const holidayData = { ...recurringHolidayData.value };

  if (holidayData.isEditing) {
    if (holidayData.editIndex !== undefined && holidayData.editIndex >= 0) {
      props.holidays[holidayData.editIndex] = { ...holidayData };
      updateWeeklyOffDates();
    } else {
      //// Neoffice — upstream wrote it in plain English; wrapped so the French catalogue reaches it (same pass as 71a5669d9)
      toast.error(__("Error: Unable to find the holiday to update"));
      return;
    }
  } else {
    const isDuplicate = props.holidays.some(
      (holiday) =>
        holiday.day === holidayData.day &&
        JSON.stringify(holiday.repetition) ===
          JSON.stringify(holidayData.repetition)
    );

    if (isDuplicate) {
      //// Neoffice — upstream wrote it in plain English; wrapped so the French catalogue reaches it (same pass as 71a5669d9)
      toast.error(__("Holiday with the same day and repetition already exists"));
      return;
    }

    props.holidays.push({
      ...holidayData,
      isEditing: false,
    });
    updateWeeklyOffDates();
  }
  dialog.value = false;
};

const deleteHoliday = (holiday: any) => {
  if (!isConfirmingDelete.value) {
    isConfirmingDelete.value = true;
    return;
  }
  const index = props.holidays.findIndex((h: any) => {
    return h.day === holiday.day;
  });
  props.holidays.splice(index, 1);
  updateWeeklyOffDates();
  dialog.value = false;
  isConfirmingDelete.value = false;
};
</script>
