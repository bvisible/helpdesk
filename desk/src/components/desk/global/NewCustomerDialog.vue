<template>
  <div>
    <!-- //// Neoffice — upstream wrote the title in plain English; wrapped so the French catalogue reaches it (same pass as 71a5669d9) -->
    <Dialog
      v-model="model"
      :options="{ title: __('Add New Customer'), size: 'sm' }"
    >
      <template #body-content>
        <div class="space-y-4">
          <!-- //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
          <div class="space-y-1">
            <Input
              v-model="state.customer"
              :label="__('Customer Name')"
              type="text"
              :placeholder="__('Tesla Inc.')"
            />
          </div>
          <!-- //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
          <div class="space-y-1">
            <!-- //// Neoffice — the placeholder's "eg:" is English too; wrapped with its sample domains (same pass as 71a5669d9) -->
            <Input
              v-model="state.domain"
              :label="__('Domain')"
              type="text"
              :placeholder="__('eg: tesla.com, mycompany.com')"
            />
          </div>
          <!-- //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
          <div class="float-end flex gap-x-2">
            <Button
              :label="__('Add')"
              theme="gray"
              variant="solid"
              @click.prevent="addCustomer"
            />
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { __ } from "@/translation";
import { Dialog, Input, createResource, toast } from "frappe-ui";
import { reactive } from "vue";

const emit = defineEmits(["customerCreated"]);
const model = defineModel<boolean>();

const state = reactive({
  customer: "",
  domain: "",
});

const customerResource = createResource({
  url: "frappe.client.insert",
  method: "POST",
  data: {
    doc: {
      doctype: "HD Customer",
      customer_name: state.customer,
      domain: state.domain,
    },
  },
  onSuccess: () => {
    state.customer = "";
    state.domain = "";
    toast.success(__("Customer created successfully."));
    emit("customerCreated");
  },
  onError: (err) => {
    toast.error(err.messages[0]);
  },
});

function addCustomer() {
  if (!state.customer) {
    //// Neoffice — upstream wrote it in plain English; wrapped so the French catalogue reaches it (same pass as 71a5669d9)
    toast.error(__("Customer name is required"));
    return;
  }
  customerResource.submit({
    doc: {
      doctype: "HD Customer",
      customer_name: state.customer,
      domain: state.domain,
    },
  });
}
</script>
