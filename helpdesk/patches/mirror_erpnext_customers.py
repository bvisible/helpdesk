# //// Neoffice — added file (no upstream equivalent).
# ////
# //// One-off catch-up for the mirror the hooks now keep: every ERPNext Customer
# //// gets its HD Customer, and every Contact already attached to a Customer gets
# //// the matching HD Customer link. Without this pass the mirror would only cover
# //// customers created AFTER the deploy, and an existing support base would stay
# //// invisible in the helpdesk — which is the whole defect being fixed.
# ////
# //// Idempotent by construction: it only creates what is missing, and it is safe to
# //// re-run (re-runnable is also how a `#v2` bump would behave later).

import frappe

from helpdesk.overrides.customer import link_contact_to_hd_customer, sync_to_hd_customer


def execute():
    if "erpnext" not in frappe.get_installed_apps():
        return
    if not frappe.db.has_column("HD Customer", "erpnext_customer"):
        # the doctype sync runs before the patches, so this should not happen —
        # but a missing column must skip, never raise: a patch that throws aborts
        # the whole migrate and every later app's after_migrate hook with it.
        return

    _mirror_customers()
    _link_contacts()


def _mirror_customers():
    customers = frappe.get_all(
        "Customer", filters={"disabled": 0}, fields=["name"], order_by="creation asc"
    )
    made = 0
    for row in customers:
        if frappe.db.exists("HD Customer", {"erpnext_customer": row.name}):
            continue
        try:
            sync_to_hd_customer(frappe.get_doc("Customer", row.name))
            made += 1
        except Exception:
            # one unmirrorable customer (a name colliding with a hand-typed support
            # customer, say) must not stop the other 233
            frappe.log_error(
                "HD Customer mirror skipped a customer",
                f"Customer: {row.name}\n\n{frappe.get_traceback()}",
            )
    frappe.db.commit()
    print(f"helpdesk: mirrored {made} ERPNext customers into HD Customer")


def _link_contacts():
    """Attach every contact that already knows its Customer.

    Reads the Dynamic Link table directly: loading 281 Contact documents to look at
    one child table each is a minute of migrate for nothing.
    """
    rows = frappe.db.sql(
        """
        SELECT dl.parent AS contact, hd.name AS hd_customer
        FROM `tabDynamic Link` dl
        JOIN `tabHD Customer` hd ON hd.erpnext_customer = dl.link_name
        WHERE dl.parenttype = 'Contact'
          AND dl.parentfield = 'links'
          AND dl.link_doctype = 'Customer'
          AND NOT EXISTS (
                SELECT 1 FROM `tabDynamic Link` existing
                WHERE existing.parent = dl.parent
                  AND existing.parenttype = 'Contact'
                  AND existing.parentfield = 'links'
                  AND existing.link_doctype = 'HD Customer'
                  AND existing.link_name = hd.name
          )
        """,
        as_dict=True,
    )
    linked = 0
    for row in rows:
        try:
            contact = frappe.get_doc("Contact", row.contact)
            link_contact_to_hd_customer(contact, "patch")
            linked += 1
        except Exception:
            frappe.log_error(
                "HD Customer link skipped a contact",
                f"Contact: {row.contact}\n\n{frappe.get_traceback()}",
            )
    frappe.db.commit()
    print(f"helpdesk: linked {linked} contacts to their support customer")
