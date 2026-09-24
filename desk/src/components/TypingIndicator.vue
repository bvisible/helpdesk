<template>
  <div v-if="typingUsers.length > 0" class="ps-2">
    <div class="flex items-center gap-2 text-sm text-ink-gray-5">
      <div class="flex items-center gap-1.5">
        <component :is="typingMessage" />
        <div class="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useTyping } from "@/composables/realtime";
import { useUserStore } from "@/stores/user";
import { computed, h, onBeforeUnmount } from "vue";
import UserAvatar from "./UserAvatar.vue";
//// Neoffice — import added for the sentences below (same pass as 71a5669d9).
import { __ } from "@/translation";

const props = defineProps({
  ticketId: {
    type: String,
    required: true,
  },
});

const { typingUsers, cleanup } = useTyping(props.ticketId);

//// Neoffice — upstream glued English fragments (" is typing", " and ", " are typing") between the
//// bold names, which no translation can reorder. Each sentence is one msgid now, with {0} / {1}
//// where the bold parts go: the TRANSLATED text is split on those placeholders and the styled
//// nodes are put back in their place, so each language keeps its own word order.
function typingSentence(message: string, parts: ReturnType<typeof h>[]) {
  return message.split(/(\{\d+\})/).map((piece) => {
    const slot = piece.match(/^\{(\d+)\}$/);
    if (slot) return parts[Number(slot[1])];
    return piece ? h("span", { class: "text-ink-gray-5" }, piece) : null;
  });
}

const typingMessage = computed(() => {
  const count = typingUsers.length;
  if (count === 0) return null;
  const { getUser } = useUserStore();
  let firstUser = getUser(typingUsers[0])?.full_name || typingUsers[0];
  console.log(firstUser);
  console.log(typingUsers);

  if (count === 1) {
    //// Neoffice — one msgid per sentence (see typingSentence above)
    return h("div", { class: "flex items-center gap-1" }, [
      h(UserAvatar, { name: typingUsers[0], size: "sm" }),
      ...typingSentence(__("{0} is typing"), [
        h("span", { class: "text-ink-gray-6 font-medium" }, firstUser),
      ]),
    ]);
  } else if (count === 2) {
    //// Neoffice — one msgid per sentence (see typingSentence above)
    return h("div", { class: "flex items-center gap-1" }, [
      ...typingSentence(__("{0} and {1} are typing"), [
        h("span", { class: "text-ink-gray-6 font-medium" }, firstUser),
        h(
          "span",
          { class: "text-ink-gray-6 font-medium" },
          getUser(typingUsers[1])?.full_name
        ),
      ]),
    ]);
  } else {
    //// Neoffice — one msgid per sentence (see typingSentence above); "N others" is its own msgid
    return h("div", { class: "flex items-center gap-1" }, [
      ...typingSentence(__("{0} and {1} are typing"), [
        h("span", { class: "text-ink-gray-6 font-medium" }, firstUser),
        h(
          "span",
          { class: "text-ink-gray-6 font-medium" },
          __("{0} others", String(count - 1))
        ),
      ]),
    ]);
  }
});

onBeforeUnmount(() => {
  cleanup();
});
</script>

<style scoped>
.typing-dots {
  display: inline-flex;
  gap: 2px;
  align-items: center;
}

.typing-dots span {
  height: 4px;
  width: 4px;
  background-color: #6b7280;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
