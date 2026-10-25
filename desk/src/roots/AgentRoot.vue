<template>
  <Layout class="isolate">
    <router-view class="flex flex-1 flex-col overflow-auto" />
  </Layout>
</template>

<script setup lang="ts">
import { useAgentStatusStore } from "@/stores/agentStatus";
import { useAuthStore } from "@/stores/auth";
import { computed, defineAsyncComponent, onBeforeMount } from "vue";
import { useRouter } from "vue-router";

import { useScreenSize } from "@/composables/screen";
//// Neoffice — import added for the onboarding switch-off below.
//// Neoffice — was "frappe-ui/frappe": upstream v1.31.0 moved useOnboarding to @framework/ui
//// (frappe-ui 1.0 no longer exports a "./frappe" subpath, the build stops on it).
import { useOnboarding } from "@framework/ui";
const router = useRouter();
const authStore = useAuthStore();
// eager: subscribes the availability socket handler and runs the login
// greeting at boot instead of on first ticket open. Guarded because a
// customer can mount this root briefly before onBeforeMount redirects them.
if (authStore.hasDeskAccess) {
  useAgentStatusStore();
}

const { isMobileView } = useScreenSize();

//// Neoffice — frappe-ui's getting-started checklist is switched off for agents.
//// Upstream registers its steps in Sidebar.vue (setUp, managers only). Our desktop
//// chrome is NeoCockpitHDSidebar, which mounts Sidebar.vue only when the cockpit
//// fails, and upstream's MobileSidebar never registers them. The editors and
//// settings screens still report steps, so with nothing registered:
////  - opening a ticket threw "Cannot read properties of undefined (reading '0')"
////    for a manager with stored steps (the status sync);
////  - a manager's comment was saved but never shown: the step update threw before
////    the editor's "submit", so the agent saw an error and would post it again.
//// Nothing in Neoffice shows the checklist, so it is marked done for this browser:
//// the composable then neither syncs nor records a step. Set here, before the
//// layouts (async components) create the editors.
const onboarding = useOnboarding("helpdesk");
if (onboarding) onboarding.isOnboardingStepsCompleted.value = true;

const MobileLayout = defineAsyncComponent(
  () => import("@/components/layouts/MobileLayout.vue")
);
const DesktopLayout = defineAsyncComponent(
  () => import("@/components/layouts/DesktopLayout.vue")
);

const Layout = computed(() => {
  if (isMobileView.value) {
    return MobileLayout;
  } else {
    return DesktopLayout;
  }
});

onBeforeMount(() => {
  if (!authStore.hasDeskAccess) {
    router.replace({ name: "TicketsCustomer" });
  }
});
</script>
