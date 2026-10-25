# //// Neoffice — added file (no upstream equivalent).
# ////
# //// Upstream's `move_contact_dynamic_link_to_hd_customer` (v1.31.0) saves every HD Customer
# //// that had a Contact linked to it, and that save loads the User of each member contact
# //// (`Contact.user`). A Contact whose user was deleted afterwards keeps pointing at it,
# //// the load throws `User ... not found`, the patch lists the customer as failed and
# //// ABORTS THE WHOLE MIGRATE of the site. Measured on the dev instance (2026-10-25):
# //// one contact left behind by a test account deleted three days earlier.
# ////
# //// So this patch runs just before it and clears the pointer to a user that does not
# //// exist. The contact keeps everything else; only a link to nothing goes. Idempotent.

import frappe


def execute():
    dangling = frappe.db.sql(
        """
        SELECT c.name
        FROM `tabContact` c
        LEFT JOIN `tabUser` u ON u.name = c.user
        WHERE IFNULL(c.user, '') != '' AND u.name IS NULL
        """,
        pluck=True,
    )
    for name in dangling:
        frappe.db.set_value("Contact", name, "user", None, update_modified=False)
    if dangling:
        print(f"helpdesk: cleared the user of {len(dangling)} contact(s) whose user no longer exists")
