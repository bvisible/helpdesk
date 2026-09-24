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
