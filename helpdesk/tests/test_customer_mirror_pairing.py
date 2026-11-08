# //// Neoffice — added file (no upstream equivalent). The junction between our
# //// one-way Customer mirror (helpdesk/overrides/customer.py) and upstream's
# //// two-way ERPNext integration (helpdesk/integrations/erpnext): both write
# //// HD Customer.erpnext_customer, and only the integration writes the back-link.

import frappe
from frappe.tests.utils import FrappeTestCase

from helpdesk.integrations.erpnext.api import sync_all_customers
from helpdesk.integrations.erpnext.test_utils import (
    disable_erpnext_sync,
    enable_erpnext_sync,
    make_erpnext_customer,
    safe_delete,
)


class TestCustomerMirrorPairing(FrappeTestCase):
    def setUp(self):
        if "erpnext" not in frappe.get_installed_apps():
            self.skipTest("ERPNext is not installed")
        if not frappe.db.has_column("Customer", "hd_customer"):
            self.skipTest("the integration's Customer.hd_customer field is absent")
        disable_erpnext_sync()
        self.addCleanup(disable_erpnext_sync)

    def test_mirror_steps_aside_when_the_integration_is_on(self):
        enable_erpnext_sync()
        erp = make_erpnext_customer("Pairing Flagged Customer")
        self.addCleanup(safe_delete, "Customer", erp.name)

        # The integration asked for no counterpart (ignore_erpnext_sync): a mirror
        # written anyway would point at the Customer with no link back.
        self.assertFalse(
            frappe.db.exists("HD Customer", {"erpnext_customer": erp.name})
        )

    def test_the_integration_adopts_what_the_mirror_wrote(self):
        erp = frappe.get_doc(
            {"doctype": "Customer", "customer_name": "Pairing Mirrored Customer"}
        ).insert(ignore_permissions=True)
        self.addCleanup(safe_delete, "Customer", erp.name)
        mirror = frappe.db.get_value(
            "HD Customer", {"erpnext_customer": erp.name}, "name"
        )
        self.assertTrue(mirror, "the mirror did not run with the integration off")
        self.addCleanup(safe_delete, "HD Customer", mirror)
        self.assertFalse(frappe.db.get_value("Customer", erp.name, "hd_customer"))

        enable_erpnext_sync()
        sync_all_customers()

        self.assertEqual(frappe.db.get_value("Customer", erp.name, "hd_customer"), mirror)
        self.assertEqual(
            frappe.db.count("HD Customer", {"erpnext_customer": erp.name}), 1
        )


class TestContactBecomesMember(FrappeTestCase):
    """Upstream v1.31.0 keeps a customer's contacts in the `contacts` child table of
    HD Customer. The mirror of the ERP Customer must fill it from the Contact's ERP link,
    or the portal shows a contact only the tickets they raised themselves."""

    def setUp(self):
        if "erpnext" not in frappe.get_installed_apps():
            self.skipTest("ERPNext is not installed")
        if not frappe.db.exists("DocType", "HD Customer Member"):
            self.skipTest("HD Customer Member is absent")
        frappe.db.set_single_value("ERPNext HD Settings", "enabled", 0)

    def test_a_contact_linked_to_the_erp_customer_joins_its_mirror(self):
        erp = frappe.get_doc(
            {"doctype": "Customer", "customer_name": "Member Mirror Customer"}
        ).insert(ignore_permissions=True)
        self.addCleanup(safe_delete, "Customer", erp.name)
        mirror = frappe.db.get_value("HD Customer", {"erpnext_customer": erp.name}, "name")
        self.assertTrue(mirror)
        self.addCleanup(safe_delete, "HD Customer", mirror)

        contact = frappe.get_doc(
            {
                "doctype": "Contact",
                "first_name": "Member",
                "last_name": "Mirror",
                "email_ids": [{"email_id": "member.mirror@example.com", "is_primary": 1}],
                "links": [{"link_doctype": "Customer", "link_name": erp.name}],
            }
        ).insert(ignore_permissions=True)
        self.addCleanup(safe_delete, "Contact", contact.name)

        members = frappe.get_all(
            "HD Customer Member",
            filters={"parent": mirror, "parenttype": "HD Customer"},
            pluck="contact_name",
        )
        self.assertEqual(members, [contact.name])

        # saving again must not add a second row
        contact.reload()
        contact.save(ignore_permissions=True)
        self.assertEqual(
            frappe.db.count("HD Customer Member", {"parent": mirror, "contact_name": contact.name}),
            1,
        )


class TestDeletingAMemberContact(FrappeTestCase):
    """Since the v1.31.0 merge a Contact is a member of its customer's mirror through a Link
    (HD Customer Member): deleting it, or the ERP Customer it belongs to, must still work and
    take it out of the mirror (drop_contact_from_hd_customers)."""

    def setUp(self):
        if "erpnext" not in frappe.get_installed_apps():
            self.skipTest("ERPNext is not installed")
        if not frappe.db.exists("DocType", "HD Customer Member"):
            self.skipTest("HD Customer Member is absent")
        frappe.db.set_single_value("ERPNext HD Settings", "enabled", 0)

    def _customer_with_a_member(self, name):
        erp = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": name,
                "customer_type": "Company",
                # ERPNext makes its primary contact from these, as the desk's quick entry does
                "email_id": f"{frappe.scrub(name)}@example.com",
            }
        ).insert(ignore_permissions=True)
        self.addCleanup(safe_delete, "Customer", erp.name)
        mirror = frappe.db.get_value("HD Customer", {"erpnext_customer": erp.name}, "name")
        self.assertTrue(mirror, "the mirror did not run")
        self.addCleanup(safe_delete, "HD Customer", mirror)
        contact = erp.customer_primary_contact or frappe.db.get_value(
            "Dynamic Link",
            {"parenttype": "Contact", "link_doctype": "Customer", "link_name": erp.name},
            "parent",
        )
        self.assertTrue(contact, "ERPNext made no contact for the customer")
        self.addCleanup(safe_delete, "Contact", contact)
        self.assertTrue(
            frappe.db.exists("HD Customer Member", {"parent": mirror, "contact_name": contact}),
            "the contact did not join the mirror",
        )
        return erp, mirror, contact

    def test_a_customer_whose_contact_is_a_member_can_be_deleted(self):
        from frappe.tests.roles import as_role

        erp, mirror, contact = self._customer_with_a_member("Member Delete Customer")
        with as_role("sales_manager"):
            frappe.delete_doc("Customer", erp.name)
        self.assertFalse(frappe.db.exists("Customer", erp.name))
        self.assertFalse(frappe.db.exists("Contact", contact))
        self.assertTrue(frappe.db.exists("HD Customer", mirror), "the mirror stays for its tickets")
        self.assertFalse(frappe.db.exists("HD Customer Member", {"contact_name": contact}))

    def test_a_primary_member_contact_can_be_deleted(self):
        from frappe.tests.roles import as_role

        _erp, mirror, contact = self._customer_with_a_member("Member Delete Contact")
        hd_customer = frappe.get_doc("HD Customer", mirror)
        hd_customer.set_primary(contact)
        hd_customer.save(ignore_permissions=True)
        with as_role("sales_manager"):
            frappe.delete_doc("Contact", contact)
        self.assertFalse(frappe.db.exists("Contact", contact))
        self.assertFalse(frappe.db.get_value("HD Customer", mirror, "primary_contact"))
        self.assertFalse(frappe.db.exists("HD Customer Member", {"contact_name": contact}))
