<template>
  <!-- //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
  <Tooltip :text="__('View documentation')">
    <a :href="url" target="_blank">
      <lucide-circle-question-mark
        class="h-4 w-4 text-ink-gray-6"
        :class="color"
      />
    </a>
  </Tooltip>
</template>

<script setup lang="ts">
defineProps<{
  url: string;
  color?: string;
}>();
</script>

<style scoped></style>
