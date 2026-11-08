# //// Neoffice — added file (no upstream equivalent).
# ////
# //// Until the v1.31.0 merge (25.10) the role `All` could create an HD Ticket: an employee of the instance who
# //// is no helpdesk agent opened a ticket to the support (« l'imprimante de l'accueil n'imprime plus »), and
# //// NORA's helpdesk_ticket_create did it for them. Upstream gave that row to `HD Customer` and `HD Customer
# //// Manager`, which a portal account gets as a member of a customer: since then only agents and customers'
# //// contacts could open one (the capability bench, ticket.create, 08.11). Jérémy, 08.11: the employees get it
# //// back, the portal accounts do not — the row is `Desk User`, the role frappe gives every account of the desk,
# //// and never `All`, which a portal account holds too. What they read stays theirs: HD Ticket's
# //// permission_query and has_permission give a non-agent their own tickets and those of the customers they
# //// manage, nothing else.
# ////
# //// The row is in hd_ticket.json (a JSON carries no marker: NEOFFICE_FORK_MARKERS.md names it). Where a
# //// Custom DocPerm set shadows the standard rights of HD Ticket (our instances, see
# //// keep_agent_roles_on_shadowed_doctypes), the JSON alone changes nothing: this patch copies the standard row
# //// into the set. Idempotent; no other role is touched.

import frappe
from frappe.permissions import rights

DOCTYPE = "HD Ticket"
ROLE = "Desk User"


def execute():
    if not frappe.db.exists("Role", ROLE):
        return  # a frappe without the automatic role of the desk
    frappe.reload_doc("helpdesk", "doctype", "hd_ticket")
    if not frappe.db.exists("Custom DocPerm", {"parent": DOCTYPE}):
        return  # the standard set applies as it is, the JSON's row with it
    if frappe.db.exists("Custom DocPerm", {"parent": DOCTYPE, "role": ROLE, "permlevel": 0}):
        return
    standard = frappe.db.get_value(
        "DocPerm", {"parent": DOCTYPE, "role": ROLE, "permlevel": 0}, list(rights), as_dict=True
    )
    if not standard or not any(standard.values()):
        return
    row = frappe.new_doc("Custom DocPerm")
    row.update({"parent": DOCTYPE, "role": ROLE, "permlevel": 0, **standard})
    row.insert(ignore_permissions=True)
    frappe.clear_cache(doctype=DOCTYPE)
    print(f"helpdesk: {ROLE} may open an HD Ticket again (Custom DocPerm set of {DOCTYPE})")
