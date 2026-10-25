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

from helpdesk.overrides.customer import sync_to_hd_customer


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
    """Make every contact that already knows its Customer a member of its HD Customer.

    Reads the Dynamic Link table directly (loading 281 Contact documents to look at one
    child table each is a minute of migrate for nothing), then saves each HD Customer
    ONCE with all its new members, since saving it grants the member role to the users.
    Runs after upstream's `move_contact_dynamic_link_to_hd_customer`, which moved the
    old Contact -> HD Customer links into the same child table.
    """
    if not frappe.db.exists("DocType", "HD Customer Member"):
        return
    rows = frappe.db.sql(
        """
        SELECT dl.parent AS contact, hd.name AS hd_customer
        FROM `tabDynamic Link` dl
        JOIN `tabHD Customer` hd ON hd.erpnext_customer = dl.link_name
        WHERE dl.parenttype = 'Contact'
          AND dl.parentfield = 'links'
          AND dl.link_doctype = 'Customer'
          AND NOT EXISTS (
                SELECT 1 FROM `tabHD Customer Member` m
                WHERE m.parent = hd.name
                  AND m.parenttype = 'HD Customer'
                  AND m.contact_name = dl.parent
          )
        """,
        as_dict=True,
    )
    by_customer = {}
    for row in rows:
        by_customer.setdefault(row.hd_customer, []).append(row.contact)
    linked = 0
    for hd_customer_name, contacts in by_customer.items():
        try:
            hd_customer = frappe.get_doc("HD Customer", hd_customer_name)
            added = [c for c in contacts if hd_customer.add_contact(c, "HD Customer")]
            if added:
                hd_customer.save(ignore_permissions=True)
                linked += len(added)
        except Exception:
            frappe.log_error(
                "HD Customer link skipped a customer",
                f"HD Customer: {hd_customer_name}\n\n{frappe.get_traceback()}",
            )
    frappe.db.commit()
    print(f"helpdesk: made {linked} contacts members of their support customer")
