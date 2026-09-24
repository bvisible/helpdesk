import { createResource } from "frappe-ui";
import type { App } from "vue";
//// Neoffice — added: a signal for the catalogue's arrival (translationsVersion below).
import { ref } from "vue";

//// Neoffice — bumped every time the catalogue lands (from the local cache, then from
//// the server). __() reads window.translatedMessages, which Vue cannot watch, so a
//// label computed before the fetch returned stayed in English for good: the menu of
//// NeoCockpitHDSidebar.vue showed Home, Knowledge Base, Customers, Contacts on a French
//// site, the catalogue arriving after layoutSettings.ts was imported. A computed that
//// reads this ref re-runs once the translations are there.
export const translationsVersion = ref(0);

//// Neoffice — resolves once the catalogue is in window.translatedMessages, when its
//// fetch fails, or after TRANSLATIONS_GRACE_MS: a slow or broken catalogue must never
//// keep the app from starting. main.js mounts the app after it, so every __() run while
//// the app is created (in setup, in a module a lazy route imports) already reads French.
//// Before, a fresh browser painted its first screen about half a second before the
//// catalogue (4.3 MB, measured on the dev instance) landed, and that screen kept its
//// English: the ticket tabs, the empty states, the menu, the module title.
const TRANSLATIONS_GRACE_MS = 3000;
let markTranslationsReady: () => void = () => {};
export const translationsReady: Promise<void> = new Promise((resolve) => {
  markTranslationsReady = resolve;
  setTimeout(resolve, TRANSLATIONS_GRACE_MS);
});

function getTranslatedMessage(message: string): string {
  const translatedMessages = (("translatedMessages" in window
    ? window["translatedMessages"]
    : null) ?? {}) as Record<string, string>;
  return translatedMessages[message] || message;
}

function translate(message: string): string;
function translate(message: string, ...args: string[]): string;
function translate(message: string, ...args: string[]): string {
  const translatedMessage = getTranslatedMessage(message);
  if (args.length === 0) {
    return translatedMessage;
  }
  return translatedMessage.replace(/{(\d+)}/g, function (match, index) {
    return typeof args[index] != "undefined" ? args[index] : match;
  });
}

export const __ = translate;

function fetchTranslations() {
  createResource({
    url: "helpdesk.api.general.get_translations",
    method: "GET",
    cache: "translations",
    auto: true,
    transform(data: Record<string, string>) {
      (window as any).translatedMessages = data;
      //// Neoffice — added: wakes the computeds that translated too early, and lets
      //// main.js mount the app (translationsVersion, translationsReady above).
      translationsVersion.value++;
      markTranslationsReady();
    },
    //// Neoffice — added: a failed fetch must not hold the app back (translationsReady).
    onError() {
      markTranslationsReady();
    },
  });
}

export function translationPlugin(app: App<Element>) {
  app.config.globalProperties.__ = translate;
  const windowObj = window as any;
  windowObj.__ = translate;
  if (!windowObj.translatedMessages) {
    fetchTranslations();
  } else {
    //// Neoffice — added branch: the catalogue is already there, nothing to wait for.
    markTranslationsReady();
  }
}

declare module "@vue/runtime-core" {
  interface ComponentCustomProperties {
    __: typeof translate;
  }
}
