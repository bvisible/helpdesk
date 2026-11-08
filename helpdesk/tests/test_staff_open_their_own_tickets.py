# //// Neoffice — added file (no upstream equivalent). See patches/staff_open_their_own_tickets.py.

from unittest.mock import patch

import frappe
from frappe.tests.roles import as_role
from frappe.tests.utils import FrappeTestCase

from helpdesk.patches.staff_open_their_own_tickets import execute
from helpdesk.utils import is_agent

DOCTYPE = "HD Ticket"
ROLE = "Desk User"


def _ticket(subject, raised_by):
    return frappe.get_doc(
        {
            "doctype": DOCTYPE,
            "subject": subject,
            "raised_by": raised_by,
            "description": "staff_open_their_own_tickets test, rolled back with the test",
        }
    )


class TestStaffOpenTheirOwnTickets(FrappeTestCase):
    """An employee of the instance who is no helpdesk agent opens a ticket to the support, as before the v1.31.0
    merge (upstream gave `create` to `All` until then); a portal account still needs to be a member of a customer."""

    def setUp(self):
        if not frappe.db.exists("Role", ROLE):
            self.skipTest(f"this frappe has no {ROLE} role")
        # what the migrate does on a site whose HD Ticket rights are a Custom DocPerm set (our instances)
        execute()
        frappe.clear_cache(doctype=DOCTYPE)
        mail = patch("frappe.sendmail")  # the acknowledgement: our fork sends at once and commits
        mail.start()
        self.addCleanup(mail.stop)

    def test_an_employee_who_is_no_agent_opens_a_ticket_and_reads_it(self):
        with as_role("sales_user") as user:
            self.assertFalse(is_agent(user))
            self.assertTrue(frappe.has_permission(DOCTYPE, "create"))
            ticket = _ticket("Staff ticket: the printer at the desk", user).insert()
            self.assertTrue(frappe.has_permission(DOCTYPE, "read", ticket.name))

    def test_an_employee_does_not_read_someone_else_s_ticket(self):
        other = _ticket("Staff ticket: someone else's", "someone-else-staff-ticket@example.com")
        other.insert(ignore_permissions=True)
        with as_role("sales_user"):
            self.assertFalse(frappe.has_permission(DOCTYPE, "read", other.name))

    def test_a_portal_account_that_belongs_to_no_customer_opens_none(self):
        email = "staff-ticket-portal@example.com"
        if not frappe.db.exists("User", email):
            frappe.get_doc(
                {"doctype": "User", "email": email, "first_name": "Portal", "user_type": "Website User",
                 "send_welcome_email": 0}
            ).insert(ignore_permissions=True)
        with as_role(email):
            self.assertFalse(frappe.has_permission(DOCTYPE, "create"))

    def test_the_patch_gives_the_row_to_a_custom_set_that_shadows_the_standard_rights(self):
        frappe.db.delete("Custom DocPerm", {"parent": DOCTYPE, "role": ROLE})
        if not frappe.db.exists("Custom DocPerm", {"parent": DOCTYPE}):
            frappe.get_doc(
                {"doctype": "Custom DocPerm", "parent": DOCTYPE, "role": "System Manager", "permlevel": 0, "read": 1}
            ).insert(ignore_permissions=True)

        execute()

        row = frappe.db.get_value(
            "Custom DocPerm",
            {"parent": DOCTYPE, "role": ROLE, "permlevel": 0},
            ["read", "write", "create", "delete", "export"],
            as_dict=True,
        )
        self.assertTrue(row and row.read and row.write and row.create)
        self.assertFalse(row.delete or row.export)
        count = frappe.db.count("Custom DocPerm", {"parent": DOCTYPE, "role": ROLE})
        execute()
        self.assertEqual(frappe.db.count("Custom DocPerm", {"parent": DOCTYPE, "role": ROLE}), count)
