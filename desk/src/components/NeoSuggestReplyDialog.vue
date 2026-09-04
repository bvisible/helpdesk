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
      <!-- //// Neoffice — .neo-suggest-dialog: CommunicationArea closes the
           editor on an outside click, and this dialog is teleported to
           <body>. The class is what puts it in the `ignore` list of that
           onClickOutside. -->
      <div class="p-5 neo-suggest-dialog">
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

        <!-- Never overwrite in silence: say it, and offer the other option. -->
        <div
          v-if="draft && hasContent"
          class="mt-3 text-p-sm text-ink-gray-6"
        >
          {{ __("Your reply already contains text — it will be replaced.") }}
        </div>

        <div class="flex items-center justify-end gap-2 mt-5">
          <Button :label="__('Close')" @click="show = false" />
          <Button
            :label="__('Regenerate')"
            :loading="suggestion.loading"
            @click="generate"
          />
          <Button
            v-if="hasContent"
            :label="__('Append')"
            :disabled="!draft || suggestion.loading"
            @click="apply('append')"
          />
          <Button
            variant="solid"
            :label="hasContent ? __('Replace') : __('Use this reply')"
            :disabled="!draft || suggestion.loading"
            @click="apply('replace')"
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
import { onMounted, ref, watch } from "vue";

const props = defineProps({
  ticketId: {
    type: [String, Number],
    default: null,
  },
  // Whether the editor already holds text. Drives "Replace" vs "Append" so the
  // agent is never surprised by where the draft lands.
  hasContent: {
    type: Boolean,
    default: false,
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

//// Neoffice — the draft is plain text, and it is drafted FROM the thread:
//// whatever the customer wrote can come back through the model verbatim. An
//// "&", a "<", or a stray "<script" in their message would then be re-emitted
//// as live markup — into the agent's rich-text editor and into the mail that
//// leaves. Escape the text first; the only markup left in the result is the
//// <p>/<br> we add ourselves. "&" must go first, or the entities produced by
//// the rules below would be escaped a second time.
function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function apply(mode = "replace") {
  // Plain text in, HTML out: the editor is a rich-text field, so keep the
  // paragraph breaks the model produced instead of collapsing them.
  const html = draft.value
    .split(/\n{2,}/)
    //// Neoffice — escapeHtml() before the wrap, never after: the paragraph is
    //// customer-derived text, the <p>/<br> is the only markup we intend.
    .map((p) => `<p>${escapeHtml(p).replace(/\n/g, "<br>")}</p>`)
    .join("");
  emit("apply", { html, mode });
  show.value = false;
}

// Draft on open, so the agent never faces an empty dialog with a button.
// onMounted, not only a watcher: the parent mounts this with v-if, so `show`
// is already true on the first render and a watcher alone never fires.
onMounted(() => {
  if (show.value && !draft.value) generate();
});
watch(show, (isOpen) => {
  if (isOpen && !draft.value) generate();
});
</script>
