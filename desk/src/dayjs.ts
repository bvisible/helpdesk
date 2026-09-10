import d from "dayjs";
import localizedFormat from "dayjs/plugin/localizedFormat";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
import { useAuthStore } from "./stores/auth";

const authStore = useAuthStore();
declare module "dayjs" {
  interface Dayjs {
    /** Example: `Aug 15, 2:29 AM` */
    short(): string;
    /** Example: `Tuesday, August 15, 2023 2:29 AM` */
    long(): string;
  }
}

d.extend(localizedFormat);
d.extend(relativeTime);
d.extend(function (_, cls) {
  cls.prototype.short = function () {
    return this.format("MMM D, h:mm A");
  };
  cls.prototype.long = function () {
    return this.format("LLLL");
  };
});
d.extend(utc);
d.extend(timezone);
d.tz.setDefault(authStore.timezone);

//// Neoffice — load the reader's dayjs locale. Upstream leaves dayjs in English, so
//// a French desk read "19 hours ago" and "2 months ago" in the middle of an
//// otherwise translated list — and those two strings can never be fixed by a PO
//// file, they are dayjs's own relative-time table.
////
//// The language has to be read SYNCHRONOUSLY: this module runs at import, long
//// before the auth store's user resource resolves, so authStore.language is still
//// empty here. frappe.boot.lang is present on the page the SPA is served from;
//// document.documentElement.lang is the fallback (it reads "en" on a French site,
//// which is a separate defect, hence the order).
////
//// The import is dynamic and per-language so Vite emits one small chunk each
//// instead of bundling every locale dayjs ships. A failure is swallowed on
//// purpose: an unknown language must leave the dates in English, never break the
//// module every screen imports.
const LOCALES: Record<string, () => Promise<unknown>> = {
  fr: () => import("dayjs/locale/fr"),
  de: () => import("dayjs/locale/de"),
  it: () => import("dayjs/locale/it"),
};

function readLanguage(): string {
  const w = window as any;
  // `window.lang` is injected by the page itself (www/helpdesk/index.py get_boot),
  // which is the only source available this early: `window.frappe` is created later
  // by the bundle, and the built index.html hardcodes lang="en" because it is a
  // build artefact. Measured: reading frappe.boot.lang here returned undefined and
  // the locale was never loaded.
  const lang = w?.lang || w?.frappe?.boot?.lang || document.documentElement.lang || "en";
  return String(lang).toLowerCase().split("-")[0];
}

const language = readLanguage();
if (LOCALES[language]) {
  LOCALES[language]()
    .then(() => d.locale(language))
    .catch(() => {
      /* unknown or unbundled locale: dates stay English, nothing else breaks */
    });
}

export const dayjs = d;
