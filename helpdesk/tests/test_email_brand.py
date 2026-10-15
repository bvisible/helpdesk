# //// Neoffice — added file (no upstream equivalent). The e-mails of the helpdesk reach our customers' customers: none
# //// of them may be signed by the upstream company (the verification e-mail said "Team Frappe", 15.10). The same
# //// render also proves the e-mail is built at all: the suite app has a file of the same path
# //// ("templates/emails/macros.html"), and it won the search, so the e-mail died on an undefined macro.

import frappe
from frappe.tests.utils import FrappeTestCase


class TestEmailBrand(FrappeTestCase):
    def test_the_verification_email_renders_signed_by_the_support_team_and_never_by_frappe(self):
        html = frappe.get_template("templates/emails/email_verification.html").render(
            {"link": "https://example.com/verify"}
        )
        self.assertIn("Support Team", html)
        self.assertNotIn("Frappe", html)
        self.assertIn("https://example.com/verify", html)
