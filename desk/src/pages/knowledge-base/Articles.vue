<template>
  <div class="p-5 pb-5 md:pb-10 px-10 w-full overflow-scroll items-center">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" class="-ms-0.5" />
      </template>
    </LayoutHeader>
    <div
      class="pt-0 sm:px-5 w-full flex flex-col gap-2 max-w-4xl 2xl:max-w-5xl"
    >
      <div
        v-if="articles.data"
        class="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-5"
      >
        <ArticleCard
          v-for="article in articles.data"
          :article="article"
          :key="article.name"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from "vue";
import { categoryName } from "@/stores/knowledgeBase";
import { Breadcrumbs, createResource, usePageMeta } from "frappe-ui";
import LayoutHeader from "@/components/LayoutHeader.vue";
import ArticleCard from "@/components/knowledge-base/ArticleCard.vue";
import { capture } from "@/telemetry";
//// Neoffice — added: __() import for the i18n pass below (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
import { __ } from "@/translation";

const props = defineProps({
  categoryId: {
    required: true,
    type: String,
  },
});

const articles = createResource({
  url: "helpdesk.api.knowledge_base.get_category_articles",
  cache: ["articles", props.categoryId],
  params: {
    category: props.categoryId,
  },
  auto: true,
});

onMounted(() => {
  categoryName.fetch({
    category: props.categoryId,
  });
  capture("kb_customer_page_articles", {
    data: {
      category: props.categoryId,
    },
  });
});

const categoryTitle = computed(() => {
  if (!categoryName.data) return;
  return categoryName.data;
});

//// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
const breadcrumbs = computed(() => {
  return [
    {
      //// Neoffice — see the block marker above: __() i18n wrap
      label: __('Knowledge Base'),
      route: {
        name: "CustomerKnowledgeBase",
      },
    },
    {
      label: categoryTitle.value,
    },
  ];
});

usePageMeta(() => {
  return {
    title: `${categoryTitle?.value}` + " - " + "Knowledge Base",
  };
});
</script>
