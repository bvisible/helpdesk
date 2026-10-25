import { createResource } from "frappe-ui";
import { computed, h, markRaw, type Component, type ComputedRef } from "vue";
import AppsIcon from "@/components/icons/AppsIcon.vue";
import { isCustomerPortal } from "@/utils";
//// Neoffice — added: __() import for the wraps below
import { __ } from "@/translation";

export interface App {
  name: string;
  logo: string;
  title: string;
  route: string;
}

const deskApp: App = {
  name: "frappe",
  logo: "/assets/helpdesk/desk/desk.png",
  //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site
  //// (a getter: this object is built at import time, before the catalogue has arrived).
  get title() {
    return __("Desk");
  },
  route: "/desk/helpdesk",
};

interface AppsMenuOption {
  label: string;
  icon: Component;
  submenu: Array<{ label: string; icon: unknown; onClick: () => void }>;
}

/**
 * Fetches the Frappe apps the user can switch to (Desk, ERPNext, CRM, ...) and
 * exposes them as a native Dropdown submenu option that opens on hover.
 *
 * Mirrors the apps switcher in frappe/builder (`DashboardSidebar.vue`): plain
 * `label`/`icon`/`onClick` items so reka's submenu hover-intent works cleanly.
 */
export function useApps() {
  const resource = createResource({
    url: "frappe.apps.get_apps",
    cache: "apps",
    // customers lack permission for get_apps (403); sidebar remounts on portal
    // switch, so this re-evaluates for agents
    auto: !isCustomerPortal.value,
    transform: (data: App[]) => {
      const apps = [deskApp];
      data.forEach((app) => {
        if (app.name === "helpdesk") return;
        apps.push({
          name: app.name,
          logo: app.logo,
          title: app.title,
          route: app.route,
        });
      });
      return apps;
    },
  });

  const apps = computed<App[]>(() => resource.data ?? []);

  const appsMenuOption: ComputedRef<AppsMenuOption> = computed(() => ({
    //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site
    label: __("Apps"),
    icon: markRaw(AppsIcon),
    submenu: apps.value.map((app) => ({
      label: app.title,
      icon: h("img", { src: app.logo }),
      onClick: () => window.open(app.route, "_self"),
    })),
  }));

  return { apps, appsMenuOption };
}
