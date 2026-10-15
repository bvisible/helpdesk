# //// Neoffice — added file (no upstream equivalent). The e-mails of the helpdesk reach our customers' customers: none
# //// of them may be signed by the upstream company (the verification e-mail said "Team Frappe", 15.10).

import frappe
from frappe.tests.utils import FrappeTestCase


class TestEmailBrand(FrappeTestCase):
    def test_the_verification_email_is_signed_by_the_support_team_and_never_by_frappe(self):
        html = frappe.get_template("templates/emails/email_verification.html").render(
            {"link": "https://example.com/verify"}
        )
        self.assertIn("Support Team", html)
        self.assertNotIn("Frappe", html)
