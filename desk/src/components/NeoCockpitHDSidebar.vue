<!-- //// Neoffice — added file (no upstream equivalent): the Helpdesk flavour of
     //// the shared chrome, and the switch that keeps upstream's Sidebar.vue
     //// reachable. It renders NeoCockpitBridge normally and falls back to
     //// upstream's <Sidebar /> the moment the cockpit bundle fails to load, so a
     //// broken/absent neoffice_theme never leaves an agent without navigation.
     //// The context nav is derived from upstream's own agentPortalSidebarOptions
     //// / customerPortalSidebarOptions, so upstream's links stay the source of
     //// truth and a new upstream entry appears here for free. Recipe: ADR-015. -->
<template>
  <Sidebar v-if="failed" />
  <NeoCockpitBridge
    v-else
    :surface-app="surfaceApp"
    :context-nav="contextNav"
    :navigate="navigate"
    :on-search="openSearch"
    search-kbd="⌘K"
    @failed="failed = true"
  />
  <CP
    v-if="!failed"
    v-model="showCommandPalette"
  />
</template>

<script setup lang="ts">
/**
 * Helpdesk flavor of the shared Neoffice chrome (NeoCockpit). Maps the
 * fixed agent/customer portal links into contextNav; the native Sidebar
 * stays as an automatic fallback. Pinned/public ticket views keep working
 * through the native fallback (they drive list state, not routes).
 * Recipe: neoffice ADR-015.
 */
import Sidebar from "@/components/layouts/Sidebar.vue";
import NeoCockpitBridge from "@/components/NeoCockpitBridge.vue";
import CP from "@/components/command-palette/CP.vue";

import {
  agentPortalSidebarOptions,
  customerPortalSidebarOptions,
} from "@/components/layouts/layoutSettings";
import { isCustomerPortal } from "@/utils";
import { useRouter, useRoute } from "vue-router";
import { ref, computed } from "vue";

const router = useRouter();
const route = useRoute();
const failed = ref(false);
const showCommandPalette = ref(false);

const surfaceApp = {
  name: "helpdesk",
  title: "Helpdesk",
  logo: "/assets/helpdesk/desk/favicon.svg",
};

// fixed links carry icon COMPONENTS — map labels to lucide strings instead
const ICONS: Record<string, string> = {
  Tickets: "lucide-ticket",
  "Knowledge Base": "lucide-book-open",
  Customers: "lucide-building",
  Contacts: "lucide-contact",
  "Call Logs": "lucide-phone",
};

function navigate(r: string) {
  if (!r) return;
  if (r.startsWith("/app") || r.startsWith("http")) window.location.href = r;
  else router.push(r);
}

const contextNav = computed(() => {
  const currentName = route.name as string;
  const links = isCustomerPortal.value
    ? customerPortalSidebarOptions
    : agentPortalSidebarOptions;
  return [
    {
      items: links.map((item: { label: string; to: string }) => ({
        label: item.label,
        icon: ICONS[item.label] || "lucide-circle",
        active:
          currentName === item.to ||
          String(currentName || "").startsWith(item.to),
        onClick: () => router.push({ name: item.to }),
      })),
    },
  ];
});

function openSearch() {
  showCommandPalette.value = true;
}
</script>
