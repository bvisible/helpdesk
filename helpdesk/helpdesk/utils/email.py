import frappe
from frappe.query_builder import DocType, Query


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
        .limit(1)
    )

    return query_get_one(r)
