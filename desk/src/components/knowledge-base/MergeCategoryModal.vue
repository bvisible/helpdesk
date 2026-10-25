<template>
  <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
  <Dialog
    :title="__('Merge with another category')"
    @after-leave="
      () => {
        toCategory = null;
      }
    "
    v-model:open="showDialog"
  >
    <template #default>
      <!-- //// Neoffice — wrapped in __(): one sentence cut around the bold category title, one msgid with {0} where the title goes, halves read back from the translation (moveNote) -->
      <p class="text-p-base text-ink-gray-8 mb-4">
        {{ moveNote.before
        }}<span class="whitespace-nowrap font-semibold">{{ categoryTitle }}</span
        >{{ moveNote.after }}
      </p>
      <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
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
//// Neoffice — i18n of the v1.31.0 merge: __() wrap or label/value split (upstream shows this string in English on every non-English site)
import { computed, ref } from "vue";
import { Dialog } from "frappe-ui";
import { Link } from "@/components";
//// Neoffice — added: __() import for the wraps below
import { __ } from "@/translation";
defineProps<{
  categoryId: string;
  categoryTitle: string;
}>();
const emit = defineEmits(["merge"]);
const showDialog = defineModel<boolean>();

const toCategory = ref("");

//// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site
//// (one message, {0} where the category title goes; the halves are read back from the translation)
const moveNote = computed(() => {
  const [before, after] = __(
    "This will move all articles of the {0} category to the selected category. This change is irreversible!"
  ).split("{0}");
  return { before, after: after ?? "" };
});
</script>
