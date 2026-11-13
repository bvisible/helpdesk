# //// Neoffice — added file (no upstream equivalent). See the marker in hd_ticket/customer_edit_controller.py.

from unittest.mock import patch

import frappe
from frappe.tests.roles import as_role
from frappe.tests.utils import FrappeTestCase

from helpdesk.utils import is_agent

DOCTYPE = "HD Ticket"
VISITOR = "server-insert-visitor@example.com"


def _ticket(subject):
    return frappe.get_doc(
        {
            "doctype": DOCTYPE,
            "subject": subject,
            "raised_by": VISITOR,
            "description": "test_a_server_insert_keeps_its_requester, rolled back with the test",
        }
    )


class TestAServerInsertKeepsItsRequester(FrappeTestCase):
    """Upstream v1.31.1 makes a non-agent the requester of every ticket they insert (a customer cannot raise one in
    someone else's name). Our server code that inserts with ignore_permissions on behalf of a third party (a website
    message made into a ticket by an employee) keeps the third party as requester."""

    def setUp(self):
        mail = patch("frappe.sendmail")  # the acknowledgement
        mail.start()
        self.addCleanup(mail.stop)

    def test_an_employee_makes_a_ticket_for_a_visitor_and_the_visitor_stays_its_requester(
        self,
    ):
        with as_role("sales_user") as user:
            self.assertFalse(is_agent(user))
            ticket = _ticket("Website message made into a ticket").insert(
                ignore_permissions=True
            )
        self.assertEqual(ticket.raised_by, VISITOR)

    def test_through_the_permission_checks_the_requester_is_still_the_one_who_inserts(
        self,
    ):
        with as_role("sales_user") as user:
            if not frappe.has_permission(DOCTYPE, "create"):
                self.skipTest(
                    "this site gives the desk users no right to open a ticket"
                )
            ticket = _ticket("A ticket raised in someone else's name").insert()
        self.assertEqual(ticket.raised_by, user)
