# //// Neoffice — added file (no upstream equivalent).
# ////
# //// Upstream keeps `HD Customer` as a doctype PARALLEL to ERPNext's `Customer`,
# //// with no link between them. On an instance that runs both, that means the
# //// Customers screen of the helpdesk is empty while the ERP holds hundreds of
# //// customers (measured on a dev instance: 234 Customer, 281 Contact,
# //// 0 HD Customer), and there is nothing to fix by hand — a support agent would
# //// have to retype the whole customer base.
# ////
# //// What it actually breaks goes past an empty screen. `HD Ticket` filters the
# //// customer portal with `customer in get_customer(user)`
# //// (permission_query_conditions): with no customer, a contact sees only the
# //// tickets they raised themselves, never their company's. One colleague away and
# //// the case is invisible.
# ////
# //// So: HD Customer becomes a MIRROR of Customer, kept by these hooks. The mirror
# //// is one-way — the ERP owns the customer, the helpdesk reflects it — and it never
# //// deletes: a Customer removed from the ERP leaves its HD Customer behind, because
# //// tickets link to it and losing that link would orphan their history.

import frappe
from frappe.utils import cint


def _domain_of(email):
    """The domain part of an email address, or None."""
    if not email or "@" not in email:
        return None
    domain = email.rsplit("@", 1)[1].strip().lower()
    return domain or None


def _customer_domain(customer_name):
    """A domain to seed HD Customer.domain with — best effort, never guessed twice.

    Upstream matches a new Contact to a customer by email domain, so the field has
    a real use; but it must not be filled with a free-mail domain, which would
    attach every gmail.com contact to one customer. The website field comes first
    because it is a company domain by construction.
    """
    free = {
        "gmail.com",
        "hotmail.com",
        "hotmail.fr",
        "outlook.com",
        "outlook.fr",
        "yahoo.com",
        "yahoo.fr",
        "bluewin.ch",
        "icloud.com",
        "me.com",
        "gmx.ch",
        "gmx.net",
        "live.com",
        "protonmail.com",
        "proton.me",
        "sunrise.ch",
        "yopmail.com",
    }

    website = frappe.db.get_value("Customer", customer_name, "website")
    if website:
        host = website.split("//")[-1].split("/")[0].strip().lower()
        host = host[4:] if host.startswith("www.") else host
        if host and host not in free:
            return host

    # else the domain of the customer's contacts, but only if they agree on one
    emails = frappe.db.sql(
        """
        SELECT DISTINCT c.email_id
        FROM `tabContact` c
        JOIN `tabDynamic Link` dl
          ON dl.parent = c.name AND dl.parenttype = 'Contact' AND dl.parentfield = 'links'
        WHERE dl.link_doctype = 'Customer' AND dl.link_name = %s AND IFNULL(c.email_id, '') != ''
        """,
        customer_name,
    )
    domains = {d for d in (_domain_of(e[0]) for e in emails) if d and d not in free}
    return domains.pop() if len(domains) == 1 else None


def _unique_customer_name(customer):
    """A name free of collision for the mirror.

    `HD Customer` autonames on `customer_name`, which is `unique: 1` — while
    ERPNext's `customer_name` is NOT unique (10 duplicates on the dev instance).
    Two homonymous customers would collapse into one support customer, and their
    tickets with them. The ERPNext `name` is the identity, so it wins; it already
    equals the commercial name for most records (183 of 234 measured) and the ERP
    itself falls back to a suffixed variant for the rest.
    """
    return customer.name


def sync_to_hd_customer(doc, method=None):
    """Create or refresh the HD Customer mirroring this Customer."""
    if not frappe.db.has_column("HD Customer", "erpnext_customer"):
        # migration has not run yet on this site — do nothing rather than write a
        # mirror that cannot be traced back
        return
    if cint(doc.get("disabled")):
        # a disabled customer keeps its mirror (tickets point at it) but stops
        # being refreshed
        return

    existing = frappe.db.get_value(
        "HD Customer", {"erpnext_customer": doc.name}, ["name", "domain", "image"], as_dict=True
    )
    wanted_name = _unique_customer_name(doc)

    if existing:
        updates = {}
        if existing.name != wanted_name and not frappe.db.exists("HD Customer", wanted_name):
            frappe.rename_doc("HD Customer", existing.name, wanted_name, force=True, show_alert=False)
            existing.name = wanted_name
        if not existing.domain:
            domain = _customer_domain(doc.name)
            if domain:
                updates["domain"] = domain
        if not existing.image and doc.get("image"):
            updates["image"] = doc.image
        if updates:
            frappe.db.set_value("HD Customer", existing.name, updates, update_modified=False)
        return

    if frappe.db.exists("HD Customer", wanted_name):
        # a support customer typed by hand before the sync existed: adopt it
        # instead of failing on the unique name
        frappe.db.set_value(
            "HD Customer", wanted_name, "erpnext_customer", doc.name, update_modified=False
        )
        return

    mirror = frappe.new_doc("HD Customer")
    mirror.customer_name = wanted_name
    mirror.erpnext_customer = doc.name
    mirror.domain = _customer_domain(doc.name)
    if doc.get("image"):
        mirror.image = doc.image
    mirror.flags.ignore_permissions = True
    mirror.insert(ignore_permissions=True)


def link_contact_to_hd_customer(doc, method=None):
    """Mirror a Contact's Customer link onto its HD Customer link.

    Upstream only ever guesses this from the email domain, in `before_insert`, and
    only when a matching HD Customer already exists — three reasons it never fired.
    The ERP already knows the answer: 259 of 281 contacts on the dev instance carry
    a `Dynamic Link` to a Customer. Follow that instead of guessing.

    Runs on update as well as insert: the customer link is usually added AFTER the
    contact is created.
    """
    if not frappe.db.has_column("HD Customer", "erpnext_customer"):
        return

    customers = [
        link.link_name
        for link in (doc.get("links") or [])
        if link.link_doctype == "Customer" and link.link_name
    ]
    if not customers:
        return

    already = {
        link.link_name
        for link in (doc.get("links") or [])
        if link.link_doctype == "HD Customer"
    }

    added = False
    for customer in customers:
        mirror = frappe.db.get_value("HD Customer", {"erpnext_customer": customer}, "name")
        if not mirror or mirror in already:
            continue
        doc.append("links", {"link_doctype": "HD Customer", "link_name": mirror})
        added = True

    # on_update must not re-save the whole document (infinite loop): write the new
    # rows straight to the child table instead.
    if added and method != "before_insert":
        for link in doc.get("links"):
            if link.link_doctype == "HD Customer" and not link.name:
                link.parent = doc.name
                link.parenttype = "Contact"
                link.parentfield = "links"
                link.db_insert()
