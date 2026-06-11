<template>
  <div class="flex h-screen w-screen">
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
import NeoCockpitHDSidebar from "@/components/NeoCockpitHDSidebar.vue";
</script>
