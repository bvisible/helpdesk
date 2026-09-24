<template>
  <div class="flex flex-col gap-4 border-b px-5 pb-3">
    <div class="flex items-start text-base leading-5">
      <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
      <div class="min-w-[126px] text-sm">{{ __("Rating") }}</div>
      <div class="">
        <StarRating :rating="ticket.feedback_rating" />
      </div>
    </div>
    <div class="flex items-start text-base leading-5" v-if="ticket.feedback">
      <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
      <div class="min-w-[126px] text-sm">{{ __("Feedback") }}</div>
      <div class="text-ink-gray-8">
        {{ ticket.feedback }}
      </div>
    </div>
    <div
      v-if="ticket.feedback_extra"
      class="flex items-start text-base leading-5"
    >
      <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
      <div class="min-w-[126px] text-sm">{{ __("Comment") }}</div>
      <div class="text-ink-gray-8">
        {{ ticket.feedback_extra }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import StarRating from "../StarRating.vue";

defineProps({
  ticket: {
    type: Object,
    required: true,
  },
});
</script>

<style scoped></style>
