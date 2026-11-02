# //// Neoffice — added file (no upstream equivalent). See setup_customer_role and set_portal_defaults in setup/install.py.

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.website.utils import get_home_page

from helpdesk.setup.install import set_portal_defaults, setup_customer_role

CUSTOMER = "_portal_home_customer@yopmail.com"
CUSTOMER_ROLES = ("HD Customer", "HD Customer Manager")


class TestThePortalHomeStaysTheSites(FrappeTestCase):
    """An install or an update of this app names no home page: a customer of a shop keeps the shop (neoffice-maintenance#2122)."""

    def setUp(self):
        self.addCleanup(frappe.set_user, "Administrator")
        self.addCleanup(frappe.cache.delete_value, "home_page")
        frappe.db.set_single_value("Portal Settings", "default_portal_home", "")
        for role in CUSTOMER_ROLES:
            frappe.db.set_value("Role", role, "home_page", "")

    def assert_no_home_page_was_written(self):
        self.assertEqual(frappe.db.get_single_value("Portal Settings", "default_portal_home") or "", "")
        for role in CUSTOMER_ROLES:
            self.assertEqual(frappe.db.get_value("Role", role, "home_page") or "", "", role)

    def test_a_fresh_install_writes_no_home_page(self):
        setup_customer_role()
        self.assert_no_home_page_was_written()

    def test_the_upgrade_patches_write_none_either(self):
        setup_customer_role(fresh_install=False)
        set_portal_defaults()
        self.assert_no_home_page_was_written()

    def test_a_customer_does_not_land_in_the_application(self):
        setup_customer_role()
        if not frappe.db.exists("User", CUSTOMER):
            frappe.get_doc(
                {
                    "doctype": "User",
                    "email": CUSTOMER,
                    "first_name": "Portal Home",
                    "user_type": "Website User",
                    "send_welcome_email": 0,
                    "roles": [{"role": "HD Customer"}],
                }
            ).insert(ignore_permissions=True)
        frappe.cache.delete_value("home_page")
        frappe.set_user(CUSTOMER)
        self.assertNotEqual(get_home_page(), "helpdesk")
