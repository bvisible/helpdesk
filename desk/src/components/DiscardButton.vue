<template>
  <Button :label="label" @click="handleDiscard" />
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
  label = "Discard",
  hideDialog = false,
  title = "Discard?",
  message = "Are you sure you want to discard this?",
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
    title: title,
    message: message,
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
