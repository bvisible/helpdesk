# //// Neoffice — added file (no upstream equivalent). Tickets are numbered on a counter
# //// of their own (HDTicket.autoname), not on the empty-prefix series that upstream's
# //// ".####" draws from and that other naming on a site consumes too.

import frappe
from frappe.tests.utils import FrappeTestCase

from helpdesk.helpdesk.doctype.hd_ticket.hd_ticket import TICKET_COUNTER
from helpdesk.test_utils import make_ticket


def _series(key):
    row = frappe.db.sql("SELECT current FROM `tabSeries` WHERE name=%s", (key,))
    return row[0][0] if row else None


def _top_ticket():
    return frappe.db.sql("SELECT MAX(CAST(name AS UNSIGNED)) FROM `tabHD Ticket`")[0][0] or 0


class TestTicketCounter(FrappeTestCase):
    def test_a_ticket_does_not_draw_from_the_shared_empty_series(self):
        # other naming on the site moved the shared series far ahead of the tickets
        frappe.db.sql(
            "INSERT INTO `tabSeries` (name, current) VALUES ('', 50000)"
            " ON DUPLICATE KEY UPDATE current = current + 50000"
        )
        shared_before = _series("")

        ticket = make_ticket(subject="Counter: shared series untouched")

        self.assertEqual(_series(""), shared_before)
        self.assertLess(int(ticket.name), 50000)

    def test_the_counter_starts_after_the_highest_ticket(self):
        make_ticket(subject="Counter: an existing ticket")
        top = _top_ticket()
        frappe.db.sql("DELETE FROM `tabSeries` WHERE name=%s", (TICKET_COUNTER,))

        ticket = make_ticket(subject="Counter: the next one")

        self.assertEqual(ticket.name, "%04d" % (top + 1))
        self.assertEqual(_series(TICKET_COUNTER), top + 1)
