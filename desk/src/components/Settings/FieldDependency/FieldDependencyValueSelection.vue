<template>
  <div
    class="flex w-full flex-1 justify-between h-full h-[420px] max-h-[420px] min-h-[420px]"
  >
    <!-- left box -->
    <!-- //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
    <div class="flex-1 flex flex-col gap-1.5">
      <span class="block text-xs text-ink-gray-5">
        {{ __("Select parent field value") }}
      </span>
      <div class="border flex-1 border-e-0 rounded-s p-2 flex flex-col gap-2">
        <template v-if="state.selectedParentField">
          <FormControl
            v-model="state.parentSearch"
            :placeholder="parentPlaceholder"
            type="text"
            class="w-full"
          >
            <template #prefix>
              <LucideSearch class="h-4 w-4 text-ink-gray-4" />
            </template>
          </FormControl>
          <div class="flex-1 overflow-y-auto hide-scrollbar basis-0">
            <ul class="max-w-[350px] overflow-y-auto">
              <li
                v-for="value in filteredParentFieldValues"
                :key="value"
                class="py-2 mb-1 px-2.5 cursor-pointer rounded flex justify-between items-center hover:bg-surface-gray-1 overflow-hidden max-w-full"
                :class="{
                  'bg-surface-gray-2 hover:bg-surface-gray-3':
                    state.currentParentSelection === value,
                }"
                @click="handleParentValueClick(value)"
              >
                <span class="text-base text-ink-gray-6 max-w-[90%] truncate">{{
                  value
                }}</span>
                <LucideChevronRight
                  class="h-4 w-4 text-ink-gray-6 rtl:rotate-180"
                  v-if="
                    getSelectedChildValueCount(value) === 0 ||
                    state.currentParentSelection === value
                  "
                />
                <Badge
                  v-else
                  :label="getSelectedChildValueCount(value)"
                  :theme="'gray'"
                  variant="subtle"
                  class="!h-4"
                />
              </li>
            </ul>
          </div>
        </template>
        <template v-else>
          <div
            class="flex flex-col items-center mt-20 h-full text-ink-gray-4 text-sm"
          >
            <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
            {{ __("Please select a parent field first") }}
          </div>
        </template>
      </div>
    </div>
    <!-- right box -->
    <div class="flex-1 flex flex-col gap-1.5">
      <span class="block text-xs text-ink-gray-5 ps-1.5">
        <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
        {{ __("Select child field value") }}
      </span>
      <div class="border flex-1 rounded-e p-2 flex flex-col gap-2">
        <template
          v-if="state.selectedChildField && state.currentParentSelection"
        >
          <FormControl
            v-model="state.childSearch"
            :placeholder="childPlaceholder"
            type="text"
            class="w-full"
          >
            <template #prefix>
              <LucideSearch class="h-4 w-4 text-ink-gray-4" />
            </template>
          </FormControl>
          <div class="flex-1 overflow-y-auto hide-scrollbar basis-0">
            <!-- Master Check box -->
            <li
              class="py-2 mb-1 px-2.5 cursor-pointer rounded flex items-center bg-surface-gray-1 hover:bg-surface-gray-2"
              @click="handleSelectAllChildValues(!toggleAllChildValues)"
            >
              <FormControl
                type="checkbox"
                :model-value="toggleAllChildValues"
                class="me-2"
              />
              <span class="text-base text-ink-gray-8 font-medium">
                {{ toggleCheckboxLabel }}
              </span>
            </li>
            <ul class="max-w-[350px] overflow-y-auto">
              <li
                v-for="value in filteredChildFieldValues"
                :key="value"
                class="py-2 mb-1 px-2.5 cursor-pointer rounded flex items-center hover:bg-surface-gray-1 max-w-full truncate"
                @click="handleChildValueClick(value)"
              >
                <FormControl
                  type="checkbox"
                  :model-value="isChildValueSelected(value)"
                  class="me-2"
                />
                <span class="text-base text-ink-gray-6">{{ value }}</span>
              </li>
            </ul>
          </div>
        </template>
        <template v-else-if="!state.selectedChildField">
          <div
            class="flex flex-col items-center mt-20 h-full text-ink-gray-4 text-sm"
          >
            <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
            {{ __("Please select a child field first") }}
          </div>
        </template>
        <template v-else>
          <div
            class="flex flex-col items-center mt-20 h-full text-ink-gray-4 text-sm"
          >
            <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
            {{ __("Please select a parent value first") }}
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FieldCriteriaState } from "@/types";
import { computed } from "vue";
//// Neoffice — import added for the placeholder / checkbox label wraps below (same pass as 71a5669d9).
import { __ } from "@/translation";

const props = defineProps<{
  isNew: boolean;
  parentFields: any[];
}>();

const state = defineModel<FieldCriteriaState>();

const filteredParentFieldValues = computed(() => {
  if (!state.value.parentSearch) return state.value.parentFieldValues;
  return state.value.parentFieldValues.filter((v) =>
    v.toLowerCase().includes(state.value.parentSearch.toLowerCase())
  );
});

const filteredChildFieldValues = computed(() => {
  if (!state.value.childSearch) return state.value.childFieldValues;
  return state.value.childFieldValues.filter((v) =>
    v.toLowerCase().includes(state.value.childSearch.toLowerCase())
  );
});

//// Neoffice — upstream wrote these placeholders in plain English (template literals); one msgid
//// each, so the French catalogue reaches them (same pass as 71a5669d9). {0} is the field's
//// label (translated like everywhere else it is shown) or the selected parent value (data).
const parentPlaceholder = computed(() => {
  if (!state.value.selectedParentField) return __("Search values");
  let label = props.parentFields.find(
    (f) => f.value === state.value.selectedParentField
  )?.label;
  //// Neoffice — see the note above parentPlaceholder
  return __("Search {0} values", __(label));
});
//// Neoffice — see the note above parentPlaceholder
const childPlaceholder = computed(() => {
  if (!state.value.currentParentSelection) return __("Search values");
  return __("Search {0} values", state.value.currentParentSelection);
});

function handleParentValueClick(value: string) {
  state.value.currentParentSelection = value;
}

function handleChildValueClick(childValue: string) {
  const parent = state.value.currentParentSelection;
  if (!parent) return;
  if (!(state.value.childSelections[parent] instanceof Set)) {
    state.value.childSelections[parent] = new Set();
  }
  if (state.value.childSelections[parent].has(childValue)) {
    state.value.childSelections[parent].delete(childValue);
  } else {
    state.value.childSelections[parent].add(childValue);
  }
}

function getSelectedChildValueCount(parent: string) {
  const selectedCount =
    state.value.childSelections[parent] instanceof Set
      ? state.value.childSelections[parent].size
      : 0;
  return selectedCount;
}

// Toggling master checkbox + child values
const toggleAllChildValues = computed({
  get() {
    const parent = state.value.currentParentSelection;
    if (!parent) return false;
    // If no child values are selected, return false
    if (!(state.value.childSelections[parent] instanceof Set)) {
      return false;
    }
    // If all filtered child values are selected, return true
    return (
      state.value.childSelections[parent].size ===
      filteredChildFieldValues.value.length
    );
  },
  set(value) {
    handleSelectAllChildValues(value);
  },
});

//// Neoffice — upstream built "N value(s) selected" from English fragments; one msgid per form
//// now, so the French catalogue reaches it (same pass as 71a5669d9).
const toggleCheckboxLabel = computed(() => {
  const parent = state.value.currentParentSelection;
  if (!parent) return __("Select All");
  const selectedCount = getSelectedChildValueCount(parent);
  //// Neoffice — see the note above toggleCheckboxLabel
  if (selectedCount === 0) return __("Select All");
  return selectedCount === 1
    ? __("{0} value selected", String(selectedCount))
    : __("{0} values selected", String(selectedCount));
});

function handleSelectAllChildValues(value: boolean) {
  const parent = state.value.currentParentSelection;
  if (!parent) return;

  if (!(state.value.childSelections[parent] instanceof Set)) {
    state.value.childSelections[parent] = new Set();
  }

  if (value) {
    // Select all child values
    filteredChildFieldValues.value.forEach((childValue) => {
      state.value.childSelections[parent].add(childValue);
    });
  } else {
    // Deselect all child values
    state.value.childSelections[parent].clear();
  }
}

function isChildValueSelected(childValue: string) {
  const parent = state.value.currentParentSelection;
  return (
    state.value.childSelections[parent] instanceof Set &&
    state.value.childSelections[parent].has(childValue)
  );
}
</script>

<style scoped></style>
