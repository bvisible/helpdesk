import frappe

# //// Neoffice — mirror_erpnext_customers: use the ERP Customer link as the
# //// primary signal for HD Customer, ahead of the domain-match fallback below
# //// (3890d1177 "feat(customers): HD Customer mirrors the ERP customer, instead of ignoring it")
from helpdesk.overrides.customer import link_contact_to_hd_customer


def before_insert(doc, method=None):
    # //// Neoffice — the ERP link comes FIRST: it is knowledge, not a guess. The
    # //// domain match below stays as the fallback for a contact that reaches the
    # //// helpdesk without ever being attached to a Customer (an email that opened
    # //// a ticket, typically). See overrides/customer.py for why the mirror exists.
    link_contact_to_hd_customer(doc, "before_insert")
    if doc.get("links"):
        # already attached to a support customer — do not add a second one from a
        # domain match, which is the weaker signal of the two
        if any(link.link_doctype == "HD Customer" for link in doc.get("links")):
            return
    if doc.email_id and "@" in doc.email_id:
        domain = doc.email_id.split("@")[1]
        hd_customers = frappe.get_all(
            "HD Customer", filters={"domain": domain}, fields=["name"]
        )
        if hd_customers:
            doc.append(
                "links",
                {"link_doctype": "HD Customer", "link_name": hd_customers[0].name},
            )
