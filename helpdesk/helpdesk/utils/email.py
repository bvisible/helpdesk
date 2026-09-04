import frappe
from frappe.query_builder import DocType, Query

#//// Neoffice — added import, for the ORDER BY in
#//// default_ticket_outgoing_email_account(). frappe.query_builder does not
#//// re-export pypika's Order, so it comes straight from pypika — the same
#//// import frappe/utils/user.py and frappe/desk/listview.py use.
from pypika import Order


def query_get_one(q: Query) -> dict:
    r = q.run(as_dict=True)

    if len(r) != 1:
        return

    return r.pop()


def default_outgoing_email_account():
    QBEmailAccount = DocType("Email Account")

    r = (
        frappe.qb.from_(QBEmailAccount)
        .select(QBEmailAccount.star)
        .where(QBEmailAccount.default_outgoing == 1)
        .limit(1)
    )

    return query_get_one(r)


def default_ticket_outgoing_email_account():
    QBEmailAccount = DocType("Email Account")
    QBImapFolder = DocType("IMAP Folder")

    r = (
        frappe.qb.from_(QBEmailAccount)
        .select(QBEmailAccount.star)
        #//// Neoffice — was upstream's `default_outgoing == 1`. This query is
        #//// already narrowed to the accounts whose IMAP folder appends to
        #//// HD Ticket, i.e. the support mailboxes; requiring default_outgoing on
        #//// top of that finds nothing on a Neoffice site, where the single
        #//// default_outgoing account is the transactional one (neoemail.ch) and
        #//// support@… is merely enable_outgoing. The function then returned None
        #//// and every ticket reply left from the transactional mailbox, which is
        #//// not polled — the customer's answer was lost. One row is still
        #//// returned (.limit(1)); the caller order in sender_email() decides.
        .where(QBEmailAccount.enable_outgoing == 1)
        .inner_join(QBImapFolder)
        .on(QBImapFolder.parent == QBEmailAccount.name)
        .where(QBImapFolder.append_to == "HD Ticket")
        #//// Neoffice — added ORDER BY. Upstream's `default_outgoing == 1` could
        #//// match a single account by construction, so its `.limit(1)` was
        #//// deterministic for free. Our wider `enable_outgoing == 1` (see the
        #//// marker above) can match SEVERAL support mailboxes, and a LIMIT with
        #//// no ORDER BY returns whichever row the storage engine hands over
        #//// first — so the mailbox a ticket answers from could change between
        #//// two calls on unchanged data. Order explicitly: prefer the account
        #//// that is also the default outgoing one, then the lowest name.
        .orderby(QBEmailAccount.default_outgoing, order=Order.desc)
        .orderby(QBEmailAccount.name, order=Order.asc)
        .limit(1)
    )

    return query_get_one(r)
