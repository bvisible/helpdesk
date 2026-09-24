<template>
  <Dialog :options="options">
    <template #body-main>
      <div class="flex flex-col items-center gap-4 p-6">
        <div class="text-xl font-medium text-ink-gray-9">
          {{ customer.doc?.name }}
        </div>
        <Avatar
          size="lg"
          :label="customer.doc?.name"
          :image="customer.doc?.image"
          class="cursor-pointer hover:opacity-80"
        />
        <div class="flex gap-2">
          <FileUploader @success="(file) => updateImage(file)">
            <template #default="{ uploading, openFileSelector }">
              <!-- //// Neoffice — upstream wrote both labels in plain English; wrapped so the French catalogue reaches them (same pass as 71a5669d9) -->
              <Button
                :label="customer.doc?.image ? __('Change photo') : __('Upload photo')"
                :loading="uploading"
                @click="openFileSelector"
              />
            </template>
          </FileUploader>
          <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
          <Button
            v-if="customer.doc?.image"
            :label="__('Remove photo')"
            @click="updateImage(null)"
          />
        </div>
        <form class="w-full" @submit.prevent="update">
          <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
          <Input v-model="domain" :label="__('Domain')" placeholder="example.com" />
        </form>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { __ } from "@/translation";
import {
  Avatar,
  createDocumentResource,
  Dialog,
  FileUploader,
  toast,
} from "frappe-ui";
import { computed } from "vue";

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(["customer-updated"]);

const domain = computed({
  get() {
    return customer.doc?.domain;
  },
  set(d: string) {
    customer.doc.domain = d;
  },
});

const customer = createDocumentResource({
  doctype: "HD Customer",
  name: props.name,
  auto: true,
  setValue: {
    onSuccess() {
      toast.success(__("Customer updated successfully."));
    },
    onError() {
      toast.error(__("Error updating customer"));
    },
  },
});

const options = computed(() => ({
  title: customer.doc?.name,
  actions: [
    // //// Neoffice — label wrapped in __() (71a5669d9 "fix(i18n): 341
    // //// visible strings of the SPA never went through __()").
    {
      label: __('Save'),
      theme: "gray",
      variant: "solid",
      onClick: () => update(),
    },
  ],
}));

async function update() {
  await customer.setValue.submit({
    domain: domain.value,
  });
  emit("customer-updated");
}

function updateImage(file) {
  customer.setValue.submit({
    image: file?.file_url || null,
  });
  emit("customer-updated");
}
</script>
