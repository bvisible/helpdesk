<template>
  <SettingsLayoutBase
    :title="__('Agents')"
    :description="__('Add, manage agents and assign roles to them.')"
  >
    <template #header-actions>
      <!-- //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()") -->
      <Button
        @click="() => setActiveSettingsTab('Invite Agents')"
        :label="__('New')"
        variant="solid"
        class="rtl:flex-row-reverse"
      >
        <template #prefix>
          <LucidePlus class="h-4 w-4 stroke-1.5" />
        </template>
      </Button>
    </template>
    <template #header-bottom>
      <div class="flex items-center gap-2 justify-between">
        <div class="relative grow">
          <Input
            :model-value="search"
            @input="search = $event"
            :placeholder="__('Search')"
            type="text"
            class="focus:ring-0 border-outline-gray-2"
            icon-left="search"
            debounce="300"
            inputClass="p-4 pe-12 rtl:pr-8"
          />
          <Button
            v-if="search"
            icon="x"
            variant="ghost"
            @click="search = ''"
            class="absolute end-1 top-1/2 -translate-y-1/2"
          />
        </div>
        <Dropdown :options="dropdownOptions" placement="right">
          <template #default="{ open }">
            <!-- //// Neoffice — shows the selected option's translated label; activeFilter keeps the
                 //// untranslated value agents.ts watches (see dropdownOptions) -->
            <Button
              :label="activeFilterLabel"
              class="flex items-center justify-between w-fit p-4"
            >
              <template #suffix>
                <FeatherIcon
                  :name="open ? 'chevron-up' : 'chevron-down'"
                  class="h-4"
                />
              </template>
            </Button>
          </template>
          <template #item-label="{ item }">
            <button
              class="group flex text-ink-gray-6 gap-4 w-full justify-between items-center rounded text-base"
              @click="item.onClick"
            >
              <div class="flex items-center justify-between flex-1">
                <span class="whitespace-nowrap">
                  {{ item.label }}
                </span>
                <!-- //// Neoffice — matched on the option's value, not its label: the label is translated now (see dropdownOptions) -->
                <FeatherIcon
                  v-if="activeFilter === item.value"
                  name="check"
                  class="size-4 text-ink-gray-7"
                />
              </div>
            </button>
          </template>
        </Dropdown>
      </div>
    </template>
    <template #content>
      <div class="grow">
        <!-- loading state -->
        <div
          v-if="agents.loading"
          class="flex mt-28 justify-between w-full h-full"
        >
          <Button
            :loading="agents.loading"
            variant="ghost"
            class="w-full"
            size="2xl"
          />
        </div>
        <!-- Empty State -->
        <!-- //// Neoffice — upstream wrote title and description in plain English; wrapped so the French catalogue reaches them (same pass as 71a5669d9) -->
        <EmptyState
          v-if="!agents.loading && !agents.data?.length"
          variant="badge"
          :icon="AgentIcon"
          :title="__('No agent found')"
          :description="
            activeFilter.length
              ? __('Change your search terms or filters')
              : __('Add one to get started.')
          "
        />
        <!-- Agent List -->
        <div
          class="w-full"
          v-if="!agents.loading && Boolean(agents.data?.length)"
        >
          <div
            class="grid grid-cols-8 items-center gap-3 text-sm text-ink-gray-5"
          >
            <div class="col-span-6 text-p-sm">{{ __("Agent name") }}</div>
          </div>
          <hr class="mt-2" />
          <div v-for="(agent, index) in agents.data" :key="agent.agent_name">
            <div class="flex items-center justify-between h-14 group rounded">
              <div class="flex items-center gap-x-3 grow">
                <Avatar
                  :image="agent.user_image"
                  :label="agent.agent_name"
                  size="xl"
                />
                <div>
                  <div class="flex items-center gap-2">
                    <p class="text-base">
                      {{ agent.agent_name }}
                    </p>
                    <Badge
                      :label="__('Inactive')"
                      :theme="'gray'"
                      :class="!agent.is_active ? 'opacity-100' : 'opacity-0'"
                      variant="subtle"
                    />
                  </div>
                  <div class="text-base text-ink-gray-6 mt-1">
                    {{ agent.name }}
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <!-- //// Neoffice — the button printed the role identifier ("Agent", "Manager") as is; translated only where it is shown, the comparisons below keep the value (same pass as 71a5669d9) -->
                <Dropdown
                  v-if="isManager"
                  class="flex justify-end items-center"
                  :options="getRoles(agent.name)"
                  :label="__(getUserRole(agent.name))"
                  :button="{
                    label: __(getUserRole(agent.name)),
                    iconRight: 'chevron-down',
                    iconLeft:
                      getUserRole(agent.name) === 'Agent'
                        ? 'user'
                        : getUserRole(agent.name) === 'Manager'
                        ? 'briefcase'
                        : null,
                  }"
                  placement="right"
                />
                <Dropdown
                  :options="getOptions(agent)"
                  :key="agent"
                  class="ms-2"
                  placement="right"
                >
                  <Button icon="more-horizontal" variant="ghost" />
                </Dropdown>
              </div>
            </div>
            <hr v-if="index !== agents.data.length - 1" />
          </div>
          <!-- Load More Button -->
          <div class="flex justify-center">
            <Button
              v-if="!agents.loading && agents.hasNextPage"
              class="mt-3.5 p-2"
              @click="() => agents.next()"
              :loading="agents.loading"
              :label="__('Load More')"
              icon-left="refresh-cw"
            />
          </div>
        </div>
      </div>
    </template>
  </SettingsLayoutBase>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/stores/auth";
import { useUserStore } from "@/stores/user";
import { Avatar, Button, call, Dropdown, FeatherIcon, toast } from "frappe-ui";
//// Neoffice — `computed` added: activeFilterLabel below (our value/label split, 559991121)
//// used it without importing it, so the built chunk called a free `computed` and the
//// Agents settings screen threw a ReferenceError as soon as it opened.
import { computed, h, onUnmounted } from "vue";
import LucideCheck from "~icons/lucide/check";
import { activeFilter, useAgents } from "./agents";
import AgentIcon from "../icons/AgentIcon.vue";
import { setActiveSettingsTab } from "./settingsModal";
import SettingsLayoutBase from "@/components/layouts/SettingsLayoutBase.vue";
import { __ } from "@/translation";

const { getUserRole, updateUserRoleCache } = useUserStore();
const { isManager } = useAuthStore();

const agentStore = useAgents();
const search = agentStore.search;
const agents = agentStore.agents;

function getRoles(agent: string) {
  const agentRole = getUserRole(agent);
  const roles = [
    {
      //// Neoffice — upstream wrote it in plain English; wrapped so the French catalogue reaches it
      //// (same pass as 71a5669d9). `role` below stays the identity sent to the server.
      label: __("Agent"),
      component: (props) =>
        RoleOption({
          role: "Agent",
          active: props.active,
          selected: agentRole === "Agent",
          icon: "user",
          onClick: () => {
            updateRole(agent, "Agent");
          },
        }),
    },
  ];
  if (isManager) {
    roles.unshift({
      //// Neoffice — see the note above: label translated, `role` kept as the identity
      label: __("Manager"),
      component: (props) =>
        RoleOption({
          role: "Manager",
          active: props.active,
          selected: agentRole === "Manager",
          icon: "briefcase",
          onClick: () => {
            updateRole(agent, "Manager");
          },
        }),
    });
  }

  return roles;
}

function RoleOption({ active, role, onClick, selected, icon = null }) {
  return h(
    "button",
    {
      class: [
        active ? "bg-surface-gray-2" : "text-ink-gray-7",

        "group flex w-full text-ink-gray-8 justify-between items-center rounded-md px-2 py-2 text-sm hover:bg-surface-gray-3",
      ],
      onClick: !selected ? onClick : null,
    },
    [
      h("div", { class: "flex gap-2" }, [
        icon
          ? h(FeatherIcon, {
              name: icon,
              class: ["h-4 w-4 shrink-0"],
              "aria-hidden": true,
            })
          : null,
        //// Neoffice — `role` is the identity ("Agent", "Manager"); translated only for display
        h("span", { class: "whitespace-nowrap" }, __(role)),
      ]),
      selected
        ? h(LucideCheck, {
            class: ["h-4 w-4 shrink-0 text-ink-gray-7"],
            "aria-hidden": true,
          })
        : null,
    ]
  );
}
function updateRole(agent: string, newRole: string) {
  const currentRole = getUserRole(agent);
  if (currentRole === newRole) {
    return;
  }

  call("helpdesk.helpdesk.doctype.hd_agent.hd_agent.update_agent_role", {
    user: agent,
    new_role: newRole,
  }).then(() => {
    updateUserRoleCache(agent, newRole);
    //// Neoffice — upstream passed a template literal to __(): a msgid built at run time never
    //// reaches the catalogue. One msgid with {0} now (same pass as 71a5669d9).
    toast.success(__("Role updated to {0} successfully.", __(newRole)));
  });
}

function getOptions(agent) {
  let filters = agentStore.filters;
  return [
    //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
    {
      label: __('Disable Agent'),
      icon: "x-circle",
      onClick: async () => {
        await agentStore.updateAgent(agent.name, 0);
        agents.reload({ ...filters, search: search.value });
      },
      condition: () => agent.is_active,
    },
    //// Neoffice — wrapped in __() so the French catalogue can translate it; upstream showed it in English on every non-English site (71a5669d9 "fix(i18n): 341 visible strings of the SPA never went through __()")
    {
      label: __('Enable Agent'),
      icon: "check-circle",
      onClick: async () => {
        await agentStore.updateAgent(agent.name, 1);
        agents.reload({ ...filters, search: search.value });
      },
      condition: () => !agent.is_active,
    },
  ];
}

//// Neoffice — `label` was both what the button showed and what activeFilter
//// stored, and agents.ts watches that value ("Active" / "Inactive") to build the
//// query. So the label could not be translated without breaking the filter, and
//// the button printed an English identifier. Split: `value` is the identity,
//// `label` is what the reader sees.
const dropdownOptions = [
  {
    value: "All",
    label: __("All"),
    onClick: () => {
      agentStore.filters["is_active"] = ["in", [0, 1]];
      activeFilter.value = "All";
    },
  },
  {
    //// Neoffice — value/label split (see the note above dropdownOptions): `value` is what
    //// activeFilter stores and agents.ts watches, `label` is translated for display.
    value: "Active",
    label: __("Active"),
    onClick: () => {
      agentStore.filters["is_active"] = ["=", 1];
      activeFilter.value = "Active";
    },
  },
  {
    //// Neoffice — value/label split (see the note above dropdownOptions): `value` is what
    //// activeFilter stores and agents.ts watches, `label` is translated for display.
    value: "Inactive",
    label: __("Inactive"),
    onClick: () => {
      agentStore.filters["is_active"] = ["=", 0];
      activeFilter.value = "Inactive";
    },
  },
];

//// Neoffice — the button showed the stored identifier; show the option's label.
const activeFilterLabel = computed(
  () => dropdownOptions.find((o) => o.value === activeFilter.value)?.label ?? activeFilter.value
);

onUnmounted(() => {
  agents.filters = {};
});
</script>
