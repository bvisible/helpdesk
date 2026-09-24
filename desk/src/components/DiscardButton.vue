<template>
  <!-- //// Neoffice — upstream wrote the default label in plain English; translated here, at render, so the French catalogue reaches it (same pass as 71a5669d9) -->
  <Button :label="label ?? __('Discard')" @click="handleDiscard" />
</template>

<script setup lang="ts">
import { globalStore } from "@/stores/globalStore";
// //// Neoffice — import added for the label translation below (71a5669d9
// //// "fix(i18n): 341 visible strings of the SPA never went through __()").
import { __ } from "@/translation";
const { $dialog } = globalStore();
const emit = defineEmits<{
  (event: "discard"): void;
}>();

const {
  //// Neoffice — upstream's English defaults removed: a props-destructure default is compiled
  //// into the component definition, where __() would run before the catalogue arrives. The
  //// fallbacks are translated where they are shown (template, handleDiscard) instead.
  label,
  hideDialog = false,
  title,
  message,
} = defineProps<{
  label?: string;
  hideDialog?: boolean;
  title?: string;
  message?: string;
}>();

function handleDiscard() {
  if (hideDialog) {
    emit("discard");
    return;
  }
  $dialog({
    //// Neoffice — upstream wrote these in plain English; wrapped so the French catalogue reaches them (same pass as 71a5669d9)
    title: title ?? __("Discard?"),
    message: message ?? __("Are you sure you want to discard this?"),
    onConfirm: ({ hideDialog }: { hideDialog: Function }) => {
      hideDialog();
    },
    actions: [
      // //// Neoffice — label wrapped in __() (71a5669d9 "fix(i18n): 341
      // //// visible strings of the SPA never went through __()").
      {
        label: __("Delete"),
        theme: "red",
        iconLeft: "trash-2",
        variant: "solid",
        onClick(close: Function) {
          emit("discard");
          close();
        },
      },
    ],
  });
}
</script>
