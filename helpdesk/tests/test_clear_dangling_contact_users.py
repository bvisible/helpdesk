# //// Neoffice — added file (no upstream equivalent). See patches/clear_dangling_contact_users.py.

import frappe
from frappe.tests.utils import FrappeTestCase

from helpdesk.patches.clear_dangling_contact_users import execute


class TestClearDanglingContactUsers(FrappeTestCase):
    def test_a_contact_pointing_at_a_deleted_user_is_cleared_and_others_are_kept(self):
        contact = frappe.get_doc(
            {"doctype": "Contact", "first_name": "Dangling", "last_name": "User"}
        ).insert(ignore_permissions=True)
        self.addCleanup(frappe.delete_doc, "Contact", contact.name, force=True)
        frappe.db.set_value("Contact", contact.name, "user", "ghost-user@example.invalid")

        kept = frappe.get_doc(
            {"doctype": "Contact", "first_name": "Kept", "last_name": "User"}
        ).insert(ignore_permissions=True)
        self.addCleanup(frappe.delete_doc, "Contact", kept.name, force=True)
        frappe.db.set_value("Contact", kept.name, "user", "Administrator")

        execute()

        self.assertFalse(frappe.db.get_value("Contact", contact.name, "user"))
        self.assertEqual(frappe.db.get_value("Contact", kept.name, "user"), "Administrator")
