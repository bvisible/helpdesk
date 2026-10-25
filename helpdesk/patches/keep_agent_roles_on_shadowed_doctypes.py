# //// Neoffice — added file (no upstream equivalent).
# ////
# //// Once ANY `Custom DocPerm` row exists for a doctype, frappe ignores that doctype's
# //// standard permissions (the JSON) altogether. Our instances carry such a set on the
# //// helpdesk doctypes (built in January/August 2026 for the first installs), and on
# //// HD Ticket it had no row for `Agent` at all: agents worked through a `All` row.
# //// Upstream v1.31.0 replaces `All` by `HD Customer` in the JSON; frappe's migrate then
# //// dropped our `All` row from the custom set, and agents lost every right on tickets
# //// (measured on the dev instance on 2026-10-25: `no access to HD Ticket through role
# //// permission` for a plain agent).
# ////
# //// This patch gives `Agent` and `Agent Manager` back, on each helpdesk doctype whose
# //// custom set lacks them while the standard permissions grant them: it copies the standard
# //// row. Nothing else is touched (no other role, no removal), and it is idempotent.

import frappe
from frappe.permissions import rights

ROLES = ("Agent", "Agent Manager")


def execute():
    doctypes = frappe.get_all("DocType", filters={"module": "Helpdesk"}, pluck="name")
    added = []
    for doctype in doctypes:
        has_custom = frappe.db.exists("Custom DocPerm", {"parent": doctype})
        if not has_custom:
            continue  # the standard set applies as it is
        for role in ROLES:
            if frappe.db.exists(
                "Custom DocPerm", {"parent": doctype, "role": role, "permlevel": 0}
            ):
                continue
            standard = frappe.db.get_value(
                "DocPerm",
                {"parent": doctype, "role": role, "permlevel": 0},
                list(rights),
                as_dict=True,
            )
            if not standard or not any(standard.values()):
                continue
            row = frappe.new_doc("Custom DocPerm")
            row.update({"parent": doctype, "role": role, "permlevel": 0, **standard})
            row.insert(ignore_permissions=True)
            added.append(f"{doctype}:{role}")
    if added:
        frappe.clear_cache()
        print(f"helpdesk: gave the standard rights back to {len(added)} role(s) of shadowed doctypes: " + ", ".join(added))
