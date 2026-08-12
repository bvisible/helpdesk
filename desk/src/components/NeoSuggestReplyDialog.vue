<!-- //// Neoffice — added file (no upstream equivalent).

     Upstream ships Saved Replies (fixed templates) but nothing that reads the
     actual thread. An agent opening a ticket still starts from a blank editor.
     This dialog asks NORA for a draft and shows it BEFORE touching the editor:
     the agent stays the author, and a suggestion they dislike leaves no trace.

     Deliberately read-only towards the ticket. Sending remains reply_via_agent,
     untouched — see nora/api/helpdesk_reply.py, which has no send path at all.
-->
<template>
  <Dialog v-model="show" :options="{ size: '2xl' }">
    <template #body>
      <div class="p-5">
        <div class="flex items-center justify-between mb-4">
          <div class="text-xl font-semibold">
            {{ __("Suggested reply") }}
          </div>
          <Badge v-if="!suggestion.loading && draft" theme="gray" variant="subtle">
            {{ __("Draft — reread before sending") }}
          </Badge>
        </div>

        <!-- Steer the draft without having to rewrite it afterwards: the most
             common need is "ask for the missing detail" or "we refund". -->
        <FormControl
          v-model="instructions"
          type="text"
          :label="__('Instruction (optional)')"
          :placeholder="__('e.g. explain the delay and offer a call')"
          class="mb-4"
          @keyup.enter="generate"
        />

        <div
          v-if="suggestion.loading"
          class="flex items-center gap-2 text-base text-ink-gray-6 py-10 justify-center"
        >
          <LoadingIndicator class="h-4 w-4" />
          {{ __("NORA is writing…") }}
        </div>

        <div
          v-else-if="errorMessage"
          class="rounded border border-red-200 bg-red-50 p-3 text-base text-red-700"
        >
          {{ errorMessage }}
        </div>

        <!-- Editable on purpose: fixing one word must not cost a round-trip.
             FormControl type=textarea rather than a bare TextArea — frappe-ui
             does not export the latter. -->
        <FormControl
          v-else-if="draft"
          v-model="draft"
          type="textarea"
          :rows="12"
          class="w-full"
        />

        <div class="flex items-center justify-end gap-2 mt-5">
          <Button :label="__('Close')" @click="show = false" />
          <Button
            :label="__('Regenerate')"
            :loading="suggestion.loading"
            @click="generate"
          />
          <Button
            variant="solid"
            :label="__('Use this reply')"
            :disabled="!draft || suggestion.loading"
            @click="apply"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import {
  Badge,
  Button,
  Dialog,
  FormControl,
  LoadingIndicator,
  createResource,
} from "frappe-ui";
import { ref, watch } from "vue";

const props = defineProps({
  ticketId: {
    type: [String, Number],
    default: null,
  },
});

const emit = defineEmits(["apply"]);
const show = defineModel<boolean>();

const draft = ref("");
const instructions = ref("");
const errorMessage = ref("");

const suggestion = createResource({
  url: "nora.api.helpdesk_reply.suggest_reply",
  makeParams: () => ({
    ticket: String(props.ticketId),
    instructions: instructions.value || "",
  }),
  onSuccess: (data) => {
    // The endpoint reports refusals in its payload (no ticket, nothing to work
    // from, model unreachable) rather than raising — surface them as-is, they
    // are already written for the agent.
    if (data?.success) {
      draft.value = data.suggestion || "";
      errorMessage.value = "";
    } else {
      draft.value = "";
      errorMessage.value = data?.error || __("Could not draft a reply");
    }
  },
  onError: (err) => {
    draft.value = "";
    errorMessage.value =
      err?.messages?.[0] || err?.message || __("Could not draft a reply");
  },
});

function generate() {
  errorMessage.value = "";
  suggestion.fetch();
}

function apply() {
  // Plain text in, HTML out: the editor is a rich-text field, so keep the
  // paragraph breaks the model produced instead of collapsing them.
  const html = draft.value
    .split(/\n{2,}/)
    .map((p) => `<p>${p.replace(/\n/g, "<br>")}</p>`)
    .join("");
  emit("apply", html);
  show.value = false;
}

// Draft on open, so the agent never faces an empty dialog with a button.
watch(show, (isOpen) => {
  if (isOpen && !draft.value) generate();
});
</script>
