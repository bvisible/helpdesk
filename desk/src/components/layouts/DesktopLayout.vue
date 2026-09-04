<template>
  <div class="flex h-screen w-screen">
    <!-- //// Neoffice — was upstream's <Sidebar />. Every Neoffice app shares the
         //// same left chrome (the NeoCockpit React bundle) so a user crosses from
         //// the desk to Helpdesk without the navigation changing shape. Falls back
         //// to upstream's <Sidebar /> on its own if the bundle cannot load. -->
    <NeoCockpitHDSidebar />
    <div class="flex-1 flex flex-col h-full overflow-auto">
      <AppHeader />
      <slot />
    </div>
    <Notifications />
    <CommandPalette />
  </div>
</template>
<script setup>
import { Notifications, CommandPalette } from "@/components";
import AppHeader from "./AppHeader.vue";
//// Neoffice — replaces upstream's `import Sidebar from "./Sidebar.vue"`.
//// NeoCockpitHDSidebar renders Sidebar.vue itself when the cockpit bundle
//// fails to load, so upstream's component is still reachable, never deleted.
import NeoCockpitHDSidebar from "@/components/NeoCockpitHDSidebar.vue";
</script>
