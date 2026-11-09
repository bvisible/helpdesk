# //// Neoffice — added file (no upstream equivalent). Holds the fix of #1988: the SLA that
# //// make_sla copies is created by the install hook only, and upstream renamed it from
# //// "Default" to "Standard", so a site installed before the rename (and every clone of it)
# //// died in before_tests, before the first test of any app. No database: frappe is mocked.

import unittest
from unittest.mock import patch

from helpdesk.consts import DEFAULT_SLA
from helpdesk.test_utils import make_sla


class TestMakeSlaSeed(unittest.TestCase):
    @patch("helpdesk.setup.install.add_default_sla")
    @patch("helpdesk.test_utils.frappe")
    def test_the_shipped_sla_is_created_when_the_site_predates_its_rename(
        self, frappe, add_default_sla
    ):
        frappe.db.exists.return_value = None

        make_sla("Copy of the shipped SLA")

        frappe.db.exists.assert_called_once_with(
            "HD Service Level Agreement", DEFAULT_SLA
        )
        add_default_sla.assert_called_once_with()

    @patch("helpdesk.setup.install.add_default_sla")
    @patch("helpdesk.test_utils.frappe")
    def test_the_shipped_sla_is_left_alone_when_the_site_has_it(
        self, frappe, add_default_sla
    ):
        frappe.db.exists.return_value = DEFAULT_SLA

        make_sla("Copy of the shipped SLA")

        add_default_sla.assert_not_called()
