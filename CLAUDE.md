# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Frappe Helpdesk is an open-source ticket management tool built on Frappe Framework (Python backend) and Frappe UI (Vue.js frontend). It provides agent/customer portals, SLAs, assignment rules, a knowledge base, and canned responses.

## Tech Stack

- **Backend**: Frappe Framework (Python 3.10+), MariaDB
- **Frontend**: Vue 3 + TypeScript SPA with Vite, Pinia for state management
- **UI Library**: frappe-ui with Tailwind CSS
- **Real-time**: Socket.IO for live updates

## Development Commands

### Backend (run from frappe-bench directory)
```bash
bench start                                    # Start backend server (port 8000)
bench --site helpdesk.test install-app helpdesk
bench build --app helpdesk
```

### Frontend (from repo root)
```bash
yarn install          # Install all dependencies
cd desk && yarn dev   # Start Vite dev server (port 8080)
cd desk && yarn build # Production build
```

### Testing
```bash
# Run all tests for a doctype
bench --site helpdesk.test run-tests --app helpdesk --doctype "HD Ticket"

# Run specific test file
bench --site helpdesk.test run-tests --app helpdesk --module helpdesk.helpdesk.doctype.hd_ticket.test_hd_ticket

# Debug script execution
bench --site helpdesk.test execute helpdesk.debug.execute
```

## Architecture

### Backend (`helpdesk/`)
- `api/` — API endpoints with `@frappe.whitelist()` decorators
- `helpdesk/doctype/` — DocType definitions (HD Ticket, HD Agent, HD Article, etc.)
- `overrides/` — Custom logic overriding standard Frappe behavior
- `extends/` — Extensions to Frappe doctypes (e.g., Assignment Rule)
- `hooks.py` — Frappe hooks for permissions, scheduler events, doc events
- `search.py` — Full-text search implementation
- `utils.py` — Shared backend utilities

### Frontend (`desk/src/`)
- `pages/` — Page components (ticket/, knowledge-base/, dashboard/)
- `components/` — Reusable Vue components
- `stores/` — Pinia stores (auth, user, ticket, etc.)
- `composables/` — Vue composables
- `router/index.ts` — Vue Router with agent/customer portal routes

### Key DocTypes
- **HD Ticket** — Core ticket entity with SLA tracking
- **HD Agent** — Helpdesk agents
- **HD Article** / **HD Article Category** — Knowledge base
- **HD Service Level Agreement** — SLA definitions
- **HD Team** — Agent teams
- **HD Canned Response** — Pre-written replies

## Code Patterns

### Backend Data Queries
```python
# Prefer query builder over get_all for new code
frappe.qb.get_query("HD Ticket", filters={"status": "Open"}, fields=["name", "subject"])
```

### Frontend Data Fetching (frappe-ui)
```typescript
// List resource
const tickets = createListResource({
  doctype: "HD Ticket",
  filters: { status: "Open" },
  fields: ["name", "subject"],
  auto: true,
});

// Document resource
const ticket = createDocumentResource({
  doctype: "HD Ticket",
  name: ticketId,
  auto: true,
});

// API calls
const apiCall = createResource({
  url: "helpdesk.api.ticket.assign_ticket_to_agent",
});
apiCall.submit({ ticket_id: id, agent_id: agent });
```

### Styling (Tailwind semantic classes)
- Background: `bg-surface-white`, `bg-surface-gray-1` to `bg-surface-gray-9`
- Text: `text-ink-gray-1` to `text-ink-gray-9`, `text-ink-black`
- Border: `border-outline-gray-1` to `border-outline-gray-5`
- Always use gray shades, never color shades for primary states

### Icons
Use Lucide icons via unplugin-icons for new components:
```vue
<template>
  <LucidePlus class="size-4" />
</template>
<script setup lang="ts">
import LucidePlus from "~icons/lucide/plus";
</script>
```

## Important Conventions

- Vue components use `<script setup lang="ts">` syntax
- API endpoints go in `helpdesk/api/` with `@frappe.whitelist()` decorator
- Translations are in `helpdesk/locale/`
- TypeScript is enabled but not in strict mode
- Use Pinia for state management, @vueuse/core for utilities
