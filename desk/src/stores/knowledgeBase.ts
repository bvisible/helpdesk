import { createResource } from "frappe-ui";
//// Neoffice — added: __() import so this store's strings can enter the French catalogue; .ts literals were invisible to the extractor before this commit (79c105405 "feat(i18n): the TypeScript strings enter the catalogue — 1311 / 1311")
import { __ } from "@/translation";

// Title
export const newArticle = createResource({
  url: "frappe.client.insert",
  makeParams({ title, content, category }) {
    return {
      doc: {
        doctype: "HD Article",
        title,
        content,
        category,
      },
    };
  },
  validate({ doc }) {
    //// Neoffice — upstream wrote these validation messages in plain English (shown to the person who
    //// submits); wrapped so the French catalogue reaches them (same pass as 71a5669d9). They run at
    //// submit time, not at import.
    if (!doc.title) throw __("Title is required");
    if (!doc.content) throw __("Content is required");
  },
});

export const updateRes = createResource({
  url: "frappe.client.set_value",
});

export const deleteRes = createResource({
  url: "frappe.client.delete",
});

export const deleteArticles = createResource({
  url: "helpdesk.api.knowledge_base.delete_articles",
  makeParams({ articles }) {
    return {
      articles,
    };
  },
  validate({ articles }) {
    //// Neoffice — validation message wrapped (see newArticle above)
    if (!articles) throw __("Articles are required");
  },
});

// Category
export const newCategory = createResource({
  url: "helpdesk.api.knowledge_base.create_category",
  makeParams({ title }) {
    return {
      title,
    };
  },
  validate({ title }) {
    //// Neoffice — validation message wrapped (see newArticle above)
    if (!title) throw __("Title is required");
  },
});

export const updateCategoryTitle = createResource({
  url: "frappe.client.set_value",
  validate({ name, value }) {
    //// Neoffice — validation message wrapped (see newArticle above)
    if (!value) throw __("Title is required");
  },
});

export const moveToCategory = createResource({
  url: "helpdesk.api.knowledge_base.move_to_category",
  makeParams({ category, articles }) {
    return {
      category,
      articles,
    };
  },
  //// Neoffice — wrapped in __() so the French catalogue can translate it; .ts literals were invisible to the extractor before this commit (79c105405 "feat(i18n): the TypeScript strings enter the catalogue — 1311 / 1311")
  validate({ category, articles }) {
    if (!category) throw { message: __('Category is required') };
    if (!articles) throw { message: __('Articles are required') };
  },
});

export const mergeCategory = createResource({
  url: "helpdesk.api.knowledge_base.merge_category",
  makeParams({ source, target }) {
    return {
      source,
      target,
    };
  },
  //// Neoffice — wrapped in __() so the French catalogue can translate it; .ts literals were invisible to the extractor before this commit (79c105405 "feat(i18n): the TypeScript strings enter the catalogue — 1311 / 1311")
  validate({ source, target }) {
    if (!source) throw { message: __('Category is required') };
    if (!target) throw { message: __('Target is required') };
  },
});

export const categories = createResource({
  url: "helpdesk.api.knowledge_base.get_categories",
  cache: ["categories"],
});

export const categoryName = createResource({
  url: "helpdesk.api.knowledge_base.get_category_title",
  cache: ["categoryName"],
  makeParams({ category }) {
    return { category };
  },
});

//feedback
export const setFeedback = createResource({
  url: "run_doc_method",
  debounce: 300,
  makeParams: ({ articleId, action }) => ({
    dt: "HD Article",
    dn: articleId,
    method: "set_feedback",
    args: {
      value: action,
    },
  }),
});

// view count
export const incrementView = createResource({
  url: "helpdesk.api.knowledge_base.increment_views",
  makeParams: ({ article }) => ({
    article,
  }),
});

