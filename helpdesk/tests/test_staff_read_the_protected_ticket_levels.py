# //// Neoffice — added file (no upstream equivalent). See patches/staff_read_the_protected_ticket_levels.py.

import frappe
from frappe.permissions import setup_custom_perms
from frappe.tests.utils import FrappeTestCase

from helpdesk.consts import (
    TICKET_INTERNAL_FIELD_PERMLEVEL,
    TICKET_VISIBLE_FIELD_PERMLEVEL,
)
from helpdesk.patches.staff_read_the_protected_ticket_levels import execute

DOCTYPE = "HD Ticket"
VISIBLE = TICKET_VISIBLE_FIELD_PERMLEVEL
INTERNAL = TICKET_INTERNAL_FIELD_PERMLEVEL
ROLES = ("Agent", "Agent Manager", "Admin", "Desk User")


def _row(role, level):
    return frappe.db.get_value(
        "Custom DocPerm",
        {"parent": DOCTYPE, "role": role, "permlevel": level, "if_owner": 0},
        ["read", "write"],
        as_dict=True,
    )


class TestStaffReadTheProtectedTicketLevels(FrappeTestCase):
    """Where a Custom DocPerm set shadows HD Ticket (our instances), upstream's harden patch gives the levels 7 and 8
    only to the roles that read level 0 when it runs. An instance whose Agent row came after it kept its agents
    without priority, SLA or the internal fields; Admin never got level 8."""

    def setUp(self):
        for role in ROLES:
            if not frappe.db.exists("Role", role):
                frappe.get_doc(
                    {"doctype": "Role", "role_name": role, "desk_access": 1}
                ).insert(ignore_permissions=True)
        setup_custom_perms(
            DOCTYPE
        )  # the shadowing set our instances carry (copies the JSON's rows)
        # the state upstream's patch left on an instance where these rows came after it: level 0 only
        frappe.db.delete(
            "Custom DocPerm",
            {
                "parent": DOCTYPE,
                "role": ["in", ROLES],
                "permlevel": ["in", [VISIBLE, INTERNAL]],
            },
        )
        for role in ROLES:
            if not _row(role, 0):
                frappe.get_doc(
                    {
                        "doctype": "Custom DocPerm",
                        "parent": DOCTYPE,
                        "role": role,
                        "permlevel": 0,
                        "read": 1,
                    }
                ).insert(ignore_permissions=True)
        frappe.clear_cache(doctype=DOCTYPE)

    def test_the_agents_read_and_write_both_levels(self):
        execute()
        for role in ("Agent", "Agent Manager"):
            for level in (VISIBLE, INTERNAL):
                row = _row(role, level)
                self.assertTrue(
                    row and row.read and row.write, f"{role} at level {level}: {row}"
                )

    def test_the_customers_administrator_reads_both_levels_and_writes_none(self):
        execute()
        for level in (VISIBLE, INTERNAL):
            row = _row("Admin", level)
            self.assertTrue(row and row.read, f"Admin at level {level}: {row}")
            self.assertFalse(row.write)

    def test_an_employee_reads_what_a_requester_reads_and_not_the_internal_fields(self):
        execute()
        row = _row("Desk User", VISIBLE)
        self.assertTrue(row and row.read and not row.write)
        self.assertIsNone(_row("Desk User", INTERNAL))

    def test_a_role_that_does_not_read_the_ticket_gets_nothing(self):
        frappe.db.delete("Custom DocPerm", {"parent": DOCTYPE, "role": "Admin"})
        execute()
        self.assertIsNone(_row("Admin", VISIBLE))
        self.assertIsNone(_row("Admin", INTERNAL))

    def test_it_runs_twice_without_adding_a_row(self):
        execute()
        count = frappe.db.count("Custom DocPerm", {"parent": DOCTYPE})
        execute()
        self.assertEqual(frappe.db.count("Custom DocPerm", {"parent": DOCTYPE}), count)
