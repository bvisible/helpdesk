<template>
  <FrappeUIProvider>
    <router-view />
  </FrappeUIProvider>
  <Dialogs />
</template>

<script setup lang="ts">
import { Dialogs } from "@/components/dialogs";
import { useConfigStore } from "@/stores/config";
//// Neoffice — upstream's useFavicon is no longer imported: see the watch on the favicon below.
import { FrappeUIProvider, setConfig, toast, useColorScheme } from "frappe-ui";
import { storeToRefs } from "pinia";
//// Neoffice — `watch` added, for the favicon below.
import { h, onMounted, watch } from "vue";
import Wifi from "~icons/lucide/wifi";
import WifiOff from "~icons/lucide/wifi-off";
import { __ } from "./translation";
import { isCustomerPortal, getBrowserTimezone } from "./utils";

const configStore = useConfigStore();
const { favicon } = storeToRefs(configStore);

//// Neoffice — upstream calls useFavicon(favicon), which writes the icon on every link[rel*=icon]: the touch icon and the
//// pinned tab of a Helpdesk put on a home screen became upstream's mark, or the site's favicon. The page comes with our icons
//// (neoffice_theme/home_screen.py): only the tab follows the site's favicon, and only when the site set one.
watch(
  favicon,
  (icon) => {
    if (!icon) return;
    document.head
      .querySelectorAll<HTMLLinkElement>('link[rel~="icon"]')
      .forEach((link) => {
        link.href = icon;
        // the type and the size of the icon the page came with, which a browser would believe
        link.removeAttribute("type");
        link.removeAttribute("sizes");
      });
  },
  { immediate: true }
);

if (!localStorage.getItem("theme")) {
  localStorage.setItem("theme", "light");
}
useColorScheme();

onMounted(() => {
  window.addEventListener("online", () => {
    toast(__("You are now online."), {
      icon: () => h(Wifi, { class: "text-ink-base" }),
    });
  });

  window.addEventListener("offline", () => {
    toast(__("You are now offline."), {
      icon: () => h(WifiOff, { class: "text-ink-base" }),
    });
  });
  !isCustomerPortal.value && setConfig("localTimezone", window.timezone?.user);
  setConfig("systemTimezone", window.timezone?.system || null);
});
</script>
