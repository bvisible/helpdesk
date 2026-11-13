# //// Neoffice — added file (no upstream equivalent).
# ////
# //// Upstream v1.31.1 moved the fields of HD Ticket to two permission levels: 7 (what the customer may read:
# //// priority, SLA, due dates, team, contact…) and 8 (what only an agent reads: internal summary, mailbox,
# //// resolution details, feedback key…). Its patch harden_hd_ticket_field_permissions writes the rows where a
# //// Custom DocPerm set shadows the JSON (every one of our instances): level 7 for each role that reads the
# //// ticket, level 8 and write only for System Manager, Agent and Agent Manager, and only for the roles that
# //// ALREADY read level 0 in the set when it runs.
# ////
# //// What that leaves out on our instances, and what this patch gives (idempotent, adds only, never removes):
# //// - `Agent` and `Agent Manager` — the staff who work the tickets (Jérémy, 28.10, maintenance#1954: whoever
# ////   holds the role works in the Helpdesk): read and write at 7 and 8, even where their level-0 row was
# ////   written after upstream's patch ran (an instance that had not yet run keep_agent_roles_on_shadowed_doctypes);
# //// - `Admin` — the customer's own administrator, who reads everything that is not the platform
# ////   (neoffice_theme/admin_role.py): read at 7 and 8, never write (Admin reads, business roles write);
# //// - `Desk User` — an employee who is no agent and opens a ticket to the support (staff_open_their_own_tickets):
# ////   read at 7, like any requester. Not 8: the Helpdesk shows a non-agent only their own tickets, and level 8
# ////   holds the agents' internal fields.
# //// A role is served only where it already reads the ticket at level 0 in the custom set; a site without that
# //// set reads the JSON, which carries the same rows for Agent, Agent Manager and Desk User.

import frappe
from frappe.permissions import add_permission, update_permission_property

from helpdesk.consts import (
    TICKET_INTERNAL_FIELD_PERMLEVEL,
    TICKET_VISIBLE_FIELD_PERMLEVEL,
)

DOCTYPE = "HD Ticket"
VISIBLE = TICKET_VISIBLE_FIELD_PERMLEVEL
INTERNAL = TICKET_INTERNAL_FIELD_PERMLEVEL

# role -> {permission level: may write}
GRANTS = {
    "Agent": {VISIBLE: True, INTERNAL: True},
    "Agent Manager": {VISIBLE: True, INTERNAL: True},
    "Admin": {VISIBLE: False, INTERNAL: False},
    "Desk User": {VISIBLE: False},
}


def execute():
    if not frappe.db.exists("Custom DocPerm", {"parent": DOCTYPE}):
        return  # the JSON applies as it is
    readers = set(
        frappe.get_all(
            "Custom DocPerm",
            filters={"parent": DOCTYPE, "permlevel": 0, "read": 1},
            pluck="role",
        )
    )
    given = []
    for role, levels in GRANTS.items():
        if role not in readers:
            continue
        for level, may_write in levels.items():
            row = frappe.db.get_value(
                "Custom DocPerm",
                {"parent": DOCTYPE, "role": role, "permlevel": level, "if_owner": 0},
                ["read", "write"],
                as_dict=True,
            )
            if not row:
                add_permission(DOCTYPE, role, permlevel=level)  # grants read
                given.append(f"{role}:{level}:read")
            elif not row.read:
                update_permission_property(
                    DOCTYPE, role, level, "read", 1, validate=False
                )
                given.append(f"{role}:{level}:read")
            if may_write and not (row and row.write):
                update_permission_property(
                    DOCTYPE, role, level, "write", 1, validate=False
                )
                given.append(f"{role}:{level}:write")
    if given:
        frappe.clear_cache(doctype=DOCTYPE)
        print(f"helpdesk: {DOCTYPE} permission levels given back: " + ", ".join(given))
