# //// Neoffice — added file (no upstream equivalent). See patches/keep_agent_roles_on_shadowed_doctypes.py.

import frappe
from frappe.tests.utils import FrappeTestCase

from helpdesk.patches.keep_agent_roles_on_shadowed_doctypes import execute

DOCTYPE = "HD Ticket"


class TestKeepAgentRolesOnShadowedDoctypes(FrappeTestCase):
    def setUp(self):
        if not frappe.db.exists("DocPerm", {"parent": DOCTYPE, "role": "Agent", "permlevel": 0}):
            self.skipTest("the standard permissions of HD Ticket do not grant Agent")

    def test_agent_gets_the_standard_rights_back_when_a_custom_set_shadows_them(self):
        # a custom set that lacks Agent: what the Neoffice instances carry on HD Ticket
        frappe.db.delete("Custom DocPerm", {"parent": DOCTYPE, "role": ["in", ["Agent", "Agent Manager"]]})
        if not frappe.db.exists("Custom DocPerm", {"parent": DOCTYPE}):
            frappe.get_doc(
                {"doctype": "Custom DocPerm", "parent": DOCTYPE, "role": "System Manager", "permlevel": 0, "read": 1}
            ).insert(ignore_permissions=True)

        execute()

        row = frappe.db.get_value(
            "Custom DocPerm",
            {"parent": DOCTYPE, "role": "Agent", "permlevel": 0},
            ["read", "write", "create"],
            as_dict=True,
        )
        self.assertTrue(row and row.read and row.write and row.create)
        # idempotent: a second run adds nothing
        count = frappe.db.count("Custom DocPerm", {"parent": DOCTYPE, "role": "Agent"})
        execute()
        self.assertEqual(frappe.db.count("Custom DocPerm", {"parent": DOCTYPE, "role": "Agent"}), count)
