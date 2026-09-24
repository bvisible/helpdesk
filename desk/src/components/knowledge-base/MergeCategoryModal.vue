<template>
  <!-- //// Neoffice — wrapped in __(): one of the three remaining attributes held out of the mechanical pass because of this file's interpolated warning sentence, wrapped by hand (41fb04e59 "fix(i18n): finish the SPA pass — my own script had read only a fragment of each template") -->
  <Dialog
    :options="{
      title: __('Merge with another category'),
    }"
    @after-leave="
      () => {
        toCategory = null;
      }
    "
    v-model="showDialog"
  >
    <template #body-content>
      <!-- //// Neoffice — was one English sentence cut in three by the interpolation.
           //// Translating the fragments cannot work: French puts the name AFTER the
           //// word "catégorie" and English before it, so no split survives both. The
           //// message is now a single translatable string carrying {0}, and the two
           //// halves are recomputed from the TRANSLATED text — which keeps the bold
           //// name without a v-html (the title comes from the database). -->
      <p class="text-p-base text-ink-gray-8 mb-4">
        {{ warning.before
        }}<span class="whitespace-nowrap font-semibold">{{ categoryTitle }}</span
        >{{ warning.after }}
      </p>
      <!-- //// Neoffice — wrapped in __(): upstream showed these strings in English on every non-English site -->
      <Link
        class="form-control"
        doctype="HD Article Category"
        :placeholder="__('Select Category')"
        v-model="toCategory"
        :label="__('Category')"
        :page-length="100"
      />
    </template>
    <template #actions>
      <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
      <Button
        class="w-full"
        variant="solid"
        :label="__('Merge')"
        @click="emit('merge', categoryId, toCategory)"
      />
    </template>
  </Dialog>
</template>
<script setup lang="ts">
//// Neoffice — added `computed`: needed by the warning computed below, which keeps the category-name interpolation translatable (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
import { computed, ref } from "vue";
import { Dialog } from "frappe-ui";
import { Link } from "@/components";
//// Neoffice — added import: __() used by the wraps in this file (41fb04e59 "fix(i18n): finish the SPA pass — my own script had read only a fragment of each template")
import { __ } from "@/translation";
defineProps<{
  categoryId: string;
  categoryTitle: string;
}>();

//// Neoffice — one message, {0} where the category name goes; the halves are read
//// back from the translation so each language keeps its own word order.
const warning = computed(() => {
  const [before, after] = __(
    "This will move all articles of the {0} category to the selected category. This change is irreversible!"
  ).split("{0}");
  return { before, after: after ?? "" };
});
const emit = defineEmits(["merge"]);
const showDialog = defineModel<boolean>();

const toCategory = ref("");
</script>
