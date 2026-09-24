<template>
  <!-- //// Neoffice — passes the tab identity: ActivityHeader showed the call actions on `title == 'Calls'`, a translated label -->
  <ActivityHeader :title="title" :tab="tab" />
  <FadedScrollableDiv
    class="flex flex-col flex-1 overflow-y-auto"
    :mask-length="20"
  >
    <div v-if="activities.length" class="activities flex-1 h-full mt-0.5">
      <div
        v-for="(activity, i) in activities"
        :key="activity.key"
        class="activity mt-2"
        tabindex="0"
        :id="activity.key"
      >
        <!-- single activity -->
        <div
          class="w-full px-6 md:px-5 grid grid-cols-[30px_minmax(auto,_1fr)] gap-2 sm:gap-4"
        >
          <div
            class="relative flex justify-center after:absolute after:start-[50%] after:top-3 after:-z-10 after:border-s after:border-outline-gray-modals"
            :class="[
              i != activities.length - 1 && 'after:h-full',
              !['email', 'feedback', 'call', 'comment'].includes(
                activity.type
              ) && 'after:top-6',
            ]"
          >
            <div
              class="z-1 flex items-center justify-center rounded-full bg-surface-white"
              :class="[
                ['email', 'feedback'].includes(activity.type)
                  ? 'my-1 h-9 w-9'
                  : 'h-6 w-6',
                !['email', 'feedback', 'call', 'comment'].includes(
                  activity.type
                ) && 'mt-[2px]',
              ]"
            >
              <Avatar
                v-if="activity.type === 'email' || activity.type === 'feedback'"
                size="lg"
                :label="activity.sender?.full_name"
                :image="getUser(activity.sender?.name).user_image"
                class="bg-surface-white absolute start-[0.7px]"
              />
              <CommentIcon
                v-else-if="activity.type === 'comment'"
                class="text-ink-gray-5 absolute start-[7.5px]"
              />
              <FeatherIcon
                v-else-if="activity.type === 'call'"
                :name="
                  activity.call_type === 'Incoming'
                    ? 'phone-incoming'
                    : 'phone-outgoing'
                "
                class="text-ink-gray-5 start-[7.5px] size-4"
              />
              <DotIcon
                v-else
                class="text-ink-gray-5 absolute start-[7.5px] top-[6px]"
              />
            </div>
          </div>
          <div
            class="mb-4 flex flex-1"
            :class="[
              i == activities.length - 1 && 'mb-5',
              !['email', 'feedback', 'call', 'comment'].includes(
                activity.type
              ) && 'mt-[2px]',
            ]"
          >
            <EmailArea
              v-if="activity.type === 'email'"
              :activity="activity"
              :show-split-option="
                !activity.isFirstEmail && ticketStatus !== 'Closed'
              "
              class="py-2 px-3"
              @reply="(e) => emit('email:reply', e)"
            />
            <CommentBox
              v-else-if="activity.type === 'comment'"
              :activity="activity"
              @update="() => emit('update')"
            />
            <CallArea
              v-else-if="activity.type === 'call'"
              :activity="activity"
            />
            <FeedbackBox
              :activity="activity"
              v-else-if="activity.type === 'feedback'"
            />
            <HistoryBox v-else :activity="activity" />
          </div>
        </div>
      </div>
    </div>
    <div
      v-else
      class="h-screen flex flex-col items-center justify-center gap-3 text-xl font-medium text-ink-gray-4"
    >
      <component :is="emptyTextIcon" class="h-7.5 w-7.5" />
      <!-- //// Neoffice — emptyText is already translated in its computed (upstream: __(emptyText), a variable the POT extractor cannot see). -->
      <span class="text-lg font-medium text-ink-gray-8">{{ emptyText }}</span>
    </div>
  </FadedScrollableDiv>
</template>

<script setup lang="ts">
import { FadedScrollableDiv } from "@/components";
import {
  ActivityIcon,
  CommentIcon,
  DotIcon,
  EmailIcon,
  PhoneIcon,
} from "@/components/icons";
import { useUserStore } from "@/stores/user";
import { TicketActivity } from "@/types";
import { isElementInViewport } from "@/utils";
import { Avatar, FeatherIcon } from "frappe-ui";
import { PropType, computed, h, inject, nextTick, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import FeedbackBox from "../ticket-agent/FeedbackBox.vue";
import CommentBox from "@/components/CommentBox.vue";
import EmailArea from "@/components/EmailArea.vue";
import HistoryBox from "@/components/HistoryBox.vue";
//// Neoffice — added import: __() used by the i18n wraps below (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
import { __ } from "@/translation";

const props = defineProps({
  activities: {
    type: Array as PropType<TicketActivity[]>,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  //// Neoffice — added prop. `title` is the tab's DISPLAY label, and the two
  //// computeds below branched on it ("Emails", "Comments", "Calls"): translated,
  //// none of them ever matched and the empty state fell back to the generic one.
  //// `tab` is the TicketTab identity the parent already has.
  tab: {
    type: String,
    default: "",
  },
  ticketStatus: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["email:reply", "update"]);

const route = useRoute();
const router = useRouter();

const { getUser } = useUserStore();
const makeCall = inject<() => void>("makeCall");

//// Neoffice — branches on `tab`, not on the title, which is a translated display
//// label. The literals are wrapped HERE: upstream wrote __(emptyText) in the
//// template, a variable the POT extractor cannot see, so none of these four
//// strings ever reached the catalogue.
const emptyText = computed(() => {
  if (props.tab === "email") return __("No email communications");
  if (props.tab === "comment") return __("No comments found");
  if (props.tab === "call") return __("No calls made");

  //// Neoffice — see the block marker above: branches on tab, not title
  return __("No activity found");
});

const emptyTextIcon = computed(() => {
  //// Neoffice — same reason as emptyText: identity, not display label.
  let icon = ActivityIcon;
  if (props.tab === "email") {
    icon = EmailIcon;
  //// Neoffice — see the block marker above: identity, not display label
  } else if (props.tab === "comment") {
    icon = CommentIcon;
  } else if (props.tab === "call") {
    icon = PhoneIcon;
  }
  return h(icon, { class: "text-ink-gray-4" });
});

onMounted(() => {
  nextTick(() => {
    document.querySelector(".activity")?.focus();
  });
});

function scrollToLatestActivity() {
  if (route.hash) {
    scrollToHash();
    return;
  }
  setTimeout(() => {
    let el: HTMLElement | null;
    let e = document.getElementsByClassName("activity");
    el = e[e.length - 1] as HTMLElement;
    if (el && !isElementInViewport(el)) {
      el.focus();
    }
  }, 200);
}
function scrollToHash() {
  const hash = route.hash;
  if (hash) {
    // Remove the # symbol
    const elementId = hash.substring(1);

    nextTick(() => {
      // Wait for activities to be rendered
      setTimeout(() => {
        const element = document.getElementById(elementId);
        if (element) {
          (element as any).scrollIntoViewIfNeeded();

          // Add highlight effect using Tailwind class
          element.classList.add("bg-yellow-100");

          // Remove highlight after 2 seconds
          setTimeout(() => {
            element.classList.remove("bg-yellow-100");
            router.replace({ hash: "" });
          }, 2000);
        }
      }, 1000);
    });
  }
}

watch(
  () => route.hash,
  () => {
    scrollToLatestActivity();
  }
);

watch(
  () => props.title,
  () => {
    scrollToLatestActivity();
  },
  { immediate: true }
);

defineExpose({
  scrollToLatestActivity,
});
</script>
<style scoped>
.activity:focus {
  outline: none;
}
</style>
