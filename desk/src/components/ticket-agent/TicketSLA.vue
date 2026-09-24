<template>
  <!-- Teleport to App Header -->
  <teleport to="#app-header">
    <div
      class="flex items-center ms-5 me-5 md:me-0 text-p-sm gap-3 text-[14px] mb-2"
    >
      <!-- Source -->
      <div class="flex items-center gap-1">
        <!-- //// Neoffice — upstream wrote the copy message in plain English (a template literal); one msgid now, so the French catalogue reaches it (same pass as 71a5669d9) -->
        <p
          @click="
            copyToClipboard(
              ticket.doc.name,
              __('Ticket #{0} copied to clipboard', ticket.doc.name)
            )
          "
          class="cursor-copy"
        >
          #{{ ticket.doc.name }}
        </p>
        <!-- Via Email -->
        <div
          v-if="!ticket.doc.via_customer_portal"
          class="text-ink-gray-5 flex items-center"
        >
          <!-- //// Neoffice — upstream wrote it in plain English; wrapped so the French catalogue reaches it (same pass as 71a5669d9) -->
          <span class="me-[4px]">{{ __("via") }}</span>
          <EmailIcon class="size-4 inline-block me-1" />
          <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
          <span>{{ __("Email") }}</span>
        </div>
        <!-- Via Portal -->
        <div v-else class="text-ink-gray-5 flex items-center">
          <!-- //// Neoffice — upstream wrote it in plain English; wrapped so the French catalogue reaches it (same pass as 71a5669d9) -->
          <span class="me-[4px]">{{ __("via") }}</span>
          <GlobeIcon class="size-4 inline-block me-1" />
          <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
          <span>{{ __("Portal") }}</span>
        </div>
      </div>
      <!-- divider -->
      <div class="border-s border-outline-gray-2 h-[13px]" />
      <!-- First Response -->
      <div class="flex items-center gap-1">
        <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
        <span>{{ __("First Response") }}</span>
        <Tooltip
          :text="dateFormat(firstResponse.date, dateTooltipFormat)"
          :hover-delay="0.25"
          :placement="'top'"
        >
          <Badge
            :label="firstResponse.label"
            variant="ghost"
            class="mt-[2px]"
            :theme="firstResponse.color"
          />
        </Tooltip>
      </div>
      <!-- divider -->
      <div class="border-s border-outline-gray-2 h-[13px]" />
      <!-- Resolution by -->
      <div class="flex items-center gap-1">
        <!-- //// Neoffice — wrapped in __(): upstream showed this string in English on every non-English site -->
        <span>{{ __("Resolution") }} </span>
        <Tooltip
          :text="dateFormat(resolutionBy.date, dateTooltipFormat)"
          :hover-delay="0.25"
          :placement="'top'"
        >
          <Badge
            v-if="resolutionBy"
            :label="resolutionBy.label"
            variant="ghost"
            class="mt-[2px]"
            :theme="
              resolutionBy.color !== 'purple' ? resolutionBy.color : undefined
            "
            :class="resolutionBy.color === 'purple' && '!text-[#6B46C1] '"
          />
        </Tooltip>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { useShortcut } from "@/composables/shortcuts";
import { TicketSymbol } from "@/types";
import {
  copyToClipboard,
  dateFormat,
  dateTooltipFormat,
  formatTime,
} from "@/utils";
import { Badge, dayjs, Tooltip } from "frappe-ui";
import { computed, inject } from "vue";
//// Neoffice — import added for the SLA labels below (same pass as 71a5669d9).
import { __ } from "@/translation";

const ticket = inject(TicketSymbol)!;

const timeFormat = {
  day: true,
  hour: true,
  minute: true,
};

// Cases:
// - if not first responded and response by is in future -> show due in
// - if first responded before response by -> show fulfilled in
// - if not first responded and response by is in past -> show overdue by
// - if first responded after response by -> show failed by
const firstResponse = computed(() => {
  if (ticket.value?.get?.loading) return { label: "", color: "", date: "" };
  if (
    !ticket.value.doc.first_responded_on &&
    dayjs().isBefore(dayjs(ticket.value.doc.response_by))
  ) {
    let responseBy = formatTimeShort(ticket.value.doc.response_by as string);
    return {
      //// Neoffice — upstream wrote every SLA label of this file in plain English (template
      //// literals); one msgid each, {0} for the duration, so the French catalogue reaches them
      //// (same pass as 71a5669d9). Seen on screen: "Overdue by 14d 23h", "Failed by 12h 34m".
      label: __("Due in {0}", responseBy),
      color: "orange",
      date: ticket.value.doc.response_by,
    };
  } else if (
    dayjs(ticket.value.doc.first_responded_on).isBefore(
      dayjs(ticket.value.doc.response_by)
    )
  ) {
    let responseTime = ticket.value?.doc?.first_response_time;
    let format =
      responseTime <= 60
        ? {
            ...timeFormat,
            second: true,
          }
        : timeFormat;
    let fulfilled =
      responseTime != null
        ? formatTime(responseTime, format)
        : formatTimeShort(
            ticket.value.doc.first_responded_on as string,
            ticket.value.doc.creation
          );
    return {
      //// Neoffice — SLA label wrapped (see the note in firstResponse)
      label: __("Fulfilled in {0}", fulfilled),
      color: "green",
      date: ticket.value.doc.first_responded_on,
    };
  } else {
    if (!ticket.value.doc.first_responded_on) {
      let responseBy = formatTimeShort(
        String(new Date()),
        ticket.value.doc.response_by as string
      );
      return {
        //// Neoffice — SLA label wrapped (see the note in firstResponse)
        label: __("Overdue by {0}", responseBy),
        color: "red",
        date: ticket.value.doc.response_by,
      };
    }

    let failed = ticket.value?.doc?.first_response_failed_by
      ? formatTime(ticket.value.doc.first_response_failed_by, timeFormat)
      : formatTimeShort(
          ticket.value.doc.first_responded_on,
          ticket.value.doc.response_by
        );
    return {
      //// Neoffice — SLA label wrapped (see the note in firstResponse)
      label: __("Failed by {0}", failed),
      color: "red",
      date: ticket.value.doc.response_by,
    };
  }
});

const resolutionBy = computed(() => {
  if (ticket.value?.get?.loading) return { label: "", color: "", date: "" };

  if (
    ticket.value.doc?.status_category === "Paused" &&
    ticket.value.doc?.on_hold_since &&
    dayjs(ticket.value.doc?.resolution_by).isAfter(
      dayjs(ticket.value.doc?.on_hold_since)
    )
  ) {
    return {
      //// Neoffice — SLA label wrapped (see the note in firstResponse)
      label: __("On Hold"),
      color: "blue",
      date: ticket.value.doc?.on_hold_since,
    };
  } else if (
    !ticket.value.doc?.resolution_date &&
    dayjs().isAfter(dayjs(ticket.value.doc?.resolution_by))
  ) {
    let overdue = formatTimeShort(
      String(new Date()),
      ticket.value.doc?.resolution_by as string
    );

    return {
      //// Neoffice — SLA label wrapped (see the note in firstResponse)
      label: __("Overdue by {0}", overdue),
      color: "red",
      date: ticket.value.doc?.resolution_by,
    };
  } else if (
    !ticket.value.doc?.resolution_date &&
    dayjs().isBefore(dayjs(ticket.value.doc?.resolution_by))
  ) {
    let resolutionBy = formatTimeShort(
      ticket.value.doc?.resolution_by as string
    );
    return {
      //// Neoffice — SLA label wrapped (see the note in firstResponse)
      label: __("Due in {0}", resolutionBy),
      color: "purple",
      date: ticket.value.doc?.resolution_by,
    };
  } else if (
    dayjs(ticket.value.doc?.resolution_date).isBefore(
      dayjs(ticket.value.doc?.resolution_by)
    )
  ) {
    let resolutionTime = ticket.value?.doc?.resolution_time;
    let format =
      resolutionTime <= 60
        ? {
            ...timeFormat,
            second: true,
          }
        : timeFormat;
    let fulfilled =
      resolutionTime != null
        ? formatTime(resolutionTime, format)
        : formatTimeShort(
            ticket.value.doc?.resolution_date as string,
            ticket.value.doc?.creation
          );
    return {
      //// Neoffice — SLA label wrapped (see the note in firstResponse)
      label: __("Fulfilled in {0}", fulfilled),
      color: "green",
      date: ticket.value.doc?.resolution_date,
    };
  } else {
    let failed = ticket.value.doc?.resolution_failed_by
      ? formatTime(ticket.value.doc?.resolution_failed_by, timeFormat)
      : formatTimeShort(
          ticket.value.doc?.resolution_by,
          ticket.value.doc?.resolution_date
        );
    return {
      //// Neoffice — SLA label wrapped (see the note in firstResponse)
      label: __("Failed by {0}", failed),
      color: "red",
      date: ticket.value.doc?.resolution_by,
    };
  }
});

function formatTimeShort(date: string, end?: string): string {
  if (!end) {
    end = dayjs().toString();
  }
  let _date = dayjs(date);
  let duration = dayjs.duration(_date.diff(dayjs(end)));

  let years = duration.years();
  let months = duration.months();
  let days = duration.days();
  let hours = duration.hours();
  let minutes = duration.minutes();

  //// Neoffice — upstream wrote the unit letters in plain English (y, mo, d, h, m); one msgid per
  //// shape so a translation can change them (French writes "j" for days), same pass as 71a5669d9
  if (years > 0) {
    return __("{0}y {1}mo", years, months);
  } else if (months > 0) {
    return __("{0}mo {1}d", months, days); //// Neoffice — see above
  } else if (days > 0) {
    return __("{0}d {1}h", days, hours); //// Neoffice — see above
  } else if (hours > 0) {
    return __("{0}h {1}m", hours, minutes); //// Neoffice — see above
  } else {
    return __("{0}m", minutes); //// Neoffice — see above
  }
}

//// Neoffice — upstream wrote both copy messages in plain English (template literals); one msgid
//// each now, so the French catalogue reaches them (same pass as 71a5669d9)
useShortcut({ meta: true, shift: true, key: "." }, () => {
  copyToClipboard(window.location.href, __("Ticket URL copied to clipboard"));
});

useShortcut({ meta: true, key: "." }, () => {
  copyToClipboard(
    ticket.value.doc.name,
    //// Neoffice — see the note above the first shortcut
    __("Ticket #{0} copied to clipboard", ticket.value.doc.name)
  );
});
</script>
