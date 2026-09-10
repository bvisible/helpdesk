import functools
import json
import re

import frappe
import phonenumbers
from bs4 import BeautifulSoup
from frappe import _
from frappe.model.document import Document
from frappe.query_builder import Order
from frappe.realtime import get_website_room
from frappe.utils import floor
from frappe.utils.safe_exec import get_safe_globals
from frappe.utils.telemetry import capture as _capture
from phonenumbers import NumberParseException
from phonenumbers import PhoneNumberFormat as PNF
from pypika import Criterion
from pypika.functions import Replace


def check_permissions(doctype, parent, doc=None):
    user = frappe.session.user

    permissions = ("select", "read")
    has_select_permission, has_read_permission = [
        frappe.has_permission(doctype, perm, user=user, doc=doc, parent_doctype=parent)
        for perm in permissions
    ]

    if not has_select_permission and not has_read_permission:
        frappe.throw(
            _("Insufficient Permission for {0}").format(doctype), frappe.PermissionError
        )


def is_admin(user: str = None) -> bool:
    """
    Check whether `user` is an admin

    :param user: User to check against, defaults to current user
    :return: Whether `user` is an admin
    """
    user = user or frappe.session.user
    return user == "Administrator"


def is_agent(user: str = None) -> bool:
    """
    Check whether `user` is an agent

    :param user: User to check against, defaults to current user
    :return: Whether `user` is an agent
    """
    user = user or frappe.session.user
    return (
        is_admin()
        or "Agent Manager" in frappe.get_roles(user)
        or "Agent" in frappe.get_roles(user)
        or bool(frappe.db.exists("HD Agent", {"name": user}))
    )


def publish_event(
    event: str,
    room: str | None = None,
    data: dict | None = None,
    user: str | None = None,
):
    """
    Publish `event` to a room with `data`

    :param event: Event name. Example: "refetch_resource"
    :param data: Data to be sent with the event
    :param user: User to send the event to, defaults to current user
    """
    room = room or get_website_room()
    user = user or frappe.session.user
    frappe.publish_realtime(
        event, message=data, room=room, after_commit=True, user=user
    )


def get_doc_room(doctype: str, name: str) -> str:
    return f"open_doc:{doctype}/{name}"


def capture_event(event: str):
    return _capture(event, "helpdesk")


def get_customer(contact: str) -> tuple[str]:
    """
    Get `Customer` from `Contact`

    :param contact: Contact which belongs to a customer
    :return: Customer `name` if available
    """
    QBDynamicLink = frappe.qb.DocType("Dynamic Link")
    QBContact = frappe.qb.DocType("Contact")
    conditions = [QBDynamicLink.parent == contact, QBContact.email_id == contact]
    return [
        i[0]
        for i in (
            frappe.qb.from_(QBDynamicLink)
            .select(QBDynamicLink.link_name)
            .where(QBDynamicLink.parentfield == "links")
            .where(QBDynamicLink.parenttype == "Contact")
            .where(QBDynamicLink.link_doctype == "HD Customer")
            .join(QBContact)
            .on(QBDynamicLink.parent == QBContact.name)
            .where(Criterion.any(conditions))
            .run()
        )
    ]


def extract_mentions(html):
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    mentions = []
    for d in soup.find_all("span", attrs={"data-type": "mention"}):
        mentions.append(
            frappe._dict(full_name=d.get("data-label"), email=d.get("data-id"))
        )
    return mentions


def alphanumeric_to_int(s: str) -> int | None:
    """
    Get int from alphanumeric string, using regex
    String example: "foo-123" -> 123


    :param s: Alphanumeric string to be searched for
    :return: Integer if a number is found
    """
    s = re.search(r"\d+", s)

    if not s:
        return

    return int(s.group(0))


def get_context(d: Document) -> dict:
    """
    Get safe context for `safe_eval`

    :param doc: `Document` to add in context
    :return: Context with `doc` and safe variables
    """
    utils = get_safe_globals().get("frappe").get("utils")
    return {
        "doc": d.as_dict(),
        "frappe": frappe._dict(utils=utils),
    }


def agent_only(fn):
    """Decorator to validate if user is an agent."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if not is_agent():
            frappe.throw(
                msg=_("You are not permitted to access this resource."),
                title=_("Not Allowed"),
                exc=frappe.PermissionError,
            )

        return fn(*args, **kwargs)

    return wrapper


def get_agents_team():
    QBTeam = frappe.qb.DocType("HD Team")
    QBTeamMember = frappe.qb.DocType("HD Team Member")

    teams = (
        frappe.qb.from_(QBTeamMember)
        .where(QBTeamMember.user == frappe.session.user)
        .join(QBTeam)
        .on(QBTeam.name == QBTeamMember.parent)
        .select(QBTeam.team_name, QBTeam.ignore_restrictions)
        .run(as_dict=True)
    )
    return teams


# //// Neoffice — added function (no upstream equivalent), never called at runtime.
# //// It exists so `bench generate-pot-file` sees these msgid and a translator can
# //// reach them. They are the labels of the paths where _() must NOT be written:
# //// `_get_filterable_fields` is wrapped in @redis_cache(), whose value is shared
# //// across users for an hour, so a translation computed inside it would hand the
# //// first caller's language to everyone. `translate_labels()` looks them up at
# //// request time instead — but a dynamic `_(label)` extracts nothing, hence this
# //// declaration. Keep it in sync when a standard_fields label is added there.
def _pot_declarations():
    return [
        _("ID"),
        _("Created By"),
        _("Created On"),
        _("Last Updated By"),
        _("Last Updated On"),
        _("Assigned to"),
        _("First Response"),
    ]


# //// Neoffice — added function (no upstream equivalent). Upstream ships every list
# //// column, sort option and filterable field with a BARE English label: the
# //// module-level constants below, `default_list_data()` on each doctype, and the
# //// `standard_fields` blocks of api/doc.py. So the whole SPA showed "Subject",
# //// "Status", "Assigned To", "Last Modified" in English on a French site, and no
# //// PO file could ever fix it — those literals are not even extracted into the POT.
# ////
# //// Wrapping them in `_()` where they are WRITTEN is not an option, and that is the
# //// whole reason this helper exists:
# ////   * the constants are evaluated at IMPORT time, so `_()` there would freeze the
# ////     language of whichever request first loaded the worker, for every user;
# ////   * saved views (HD View) PERSIST their columns, labels included — a translated
# ////     label would be written into the database as data;
# ////   * `get_filterable_fields` is wrapped in `@redis_cache()`, whose key is
# ////     `module.qualname::hash(args)` with no language and no user, so a translation
# ////     computed inside it would be served to everyone for an hour.
# ////
# //// Translating on the way OUT keeps the stored/cached value English and stable while
# //// the screen follows the reader's language. It is also upstream's own pattern —
# //// `get_quick_filters()` already does `_(field.label)`; it was simply never applied
# //// to the columns. Never mutates its input: the constants are shared globals.
def translate_labels(entries):
    """Copy `entries`, translating each `label` (and Select option labels).

    `options` is a doctype name for Link fields (left alone) and a list of
    ``{label, value}`` for Select fields, where only the label is translated —
    the value is what the filter sends back to the server.
    """
    if not entries:
        return entries

    translated = []
    for entry in entries:
        if not isinstance(entry, dict):
            translated.append(entry)
            continue
        copy = dict(entry)
        if copy.get("label"):
            copy["label"] = _(copy["label"])
        options = copy.get("options")
        if isinstance(options, list):
            copy["options"] = [
                {**option, "label": _(option["label"])}
                if isinstance(option, dict) and option.get("label")
                else option
                for option in options
            ]
        translated.append(copy)
    return translated


# //// Neoffice — was a module-level LIST, now a function. The labels have to go
# //// through _(), and a constant is evaluated at import: the first request to load
# //// the worker would have frozen its language for every later caller. A function
# //// is evaluated per call, so each reader gets their own language — and the
# //// literals now reach the POT extractor, which a bare "Name" never did.
def contact_default_columns():
    return [
        {
            "label": _("Name"),
            "type": "Data",
            "key": "full_name",
            "width": "17rem",
        },
        {
            "label": _("Email"),
            "type": "Data",
            "key": "email_id",
            "width": "24rem",
        },
        {
            "label": _("Created On"),
            "type": "Datetime",
            "key": "creation",
            "width": "8rem",
        },
    ]

# //// Neoffice — was a module-level LIST, now a function, for the same two
# //// reasons as contact_default_columns above: _() must not run at import
# //// (it would pin one language per worker) and a bare literal never reaches
# //// the POT. The call-log list showed "Caller", "Receiver", "Duration",
# //// "From (number)" in English on a French desk.
def call_log_default_columns():
    return [
        {
            "label": _("Name"),
            "type": "Data",
            "key": "name",
            "width": "9rem",
        },
        {
            "label": _("Caller"),
            "type": "Link",
            "key": "caller",
            "options": "User",
            "width": "12rem",
        },
        {
            "label": _("Receiver"),
            "type": "Link",
            "key": "receiver",
            "options": "User",
            "width": "12rem",
        },
        {
            "label": _("Type"),
            "type": "Select",
            "key": "type",
            "width": "9rem",
        },
        {
            "label": _("Medium"),
            "type": "Select",
            "key": "telephony_medium",
            "width": "9rem",
        },
        {
            "label": _("Status"),
            "type": "Select",
            "key": "status",
            "width": "9rem",
        },
        {
            "label": _("Duration"),
            "type": "Duration",
            "key": "duration",
            "width": "6rem",
        },
        {
            "label": _("From (number)"),
            "type": "Data",
            "key": "from",
            "width": "9rem",
        },
        {
            "label": _("To (number)"),
            "type": "Data",
            "key": "to",
            "width": "9rem",
        },
        {
            "label": _("Created On"),
            "type": "Datetime",
            "key": "creation",
            "width": "8rem",
        },
    ]


def seconds_to_duration(seconds):
    if not seconds:
        return "0s"

    hours = floor(seconds // 3600)
    minutes = floor((seconds % 3600) // 60)
    seconds = floor((seconds % 3600) % 60)

    # 1h 0m 0s -> 1h
    # 0h 1m 0s -> 1m
    # 0h 0m 1s -> 1s
    # 1h 1m 0s -> 1h 1m
    # 1h 0m 1s -> 1h 1s
    # 0h 1m 1s -> 1m 1s
    # 1h 1m 1s -> 1h 1m 1s

    if hours and minutes and seconds:
        return f"{hours}h {minutes}m {seconds}s"
    elif hours and minutes:
        return f"{hours}h {minutes}m"
    elif hours and seconds:
        return f"{hours}h {seconds}s"
    elif minutes and seconds:
        return f"{minutes}m {seconds}s"
    elif hours:
        return f"{hours}h"
    elif minutes:
        return f"{minutes}m"
    elif seconds:
        return f"{seconds}s"
    else:
        return "0s"


def parse_phone_number(phone_number, default_country="IN"):
    try:
        # Parse the number
        number = phonenumbers.parse(phone_number, default_country)

        # Get various information about the number
        result = {
            "is_valid": phonenumbers.is_valid_number(number),
            "country_code": number.country_code,
            "national_number": str(number.national_number),
            "formats": {
                "international": phonenumbers.format_number(number, PNF.INTERNATIONAL),
                "national": phonenumbers.format_number(number, PNF.NATIONAL),
                "E164": phonenumbers.format_number(number, PNF.E164),
                "RFC3966": phonenumbers.format_number(number, PNF.RFC3966),
            },
            "type": phonenumbers.number_type(number),
            "country": phonenumbers.region_code_for_number(number),
            "is_possible": phonenumbers.is_possible_number(number),
        }

        return {"success": True, **result}
    except NumberParseException as e:
        return {"success": False, "error": str(e)}


def get_contact(phone_number):
    if not phone_number:
        return {"mobile_no": phone_number}

    cleaned_number = (
        phone_number.strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
    )

    # Check if the number is associated with a contact
    Contact = frappe.qb.DocType("Contact")
    normalized_phone = Replace(
        Replace(
            Replace(Replace(Replace(Contact.phone, " ", ""), "-", ""), "(", ""), ")", ""
        ),
        "+",
        "",
    )
    query = (
        frappe.qb.from_(Contact)
        .select(Contact.name, Contact.full_name, Contact.image, Contact.phone)
        .where(normalized_phone.like(f"%{cleaned_number}%"))
        .orderby("modified", order=Order.desc)
    )
    contacts = query.run(as_dict=True)
    return contacts[0] if contacts else {"mobile_no": phone_number}


def get_contact_by_phone_number(phone_number):
    """Get contact by phone number."""
    number = parse_phone_number(phone_number)
    if number.get("is_valid"):
        return get_contact(number.get("national_number"))
    else:
        return get_contact(phone_number)


def parse_call_log(call):
    call["show_recording"] = False
    call["_duration"] = seconds_to_duration(call.get("duration"))
    # //// Neoffice — "Unknown" reached the call list in English, and the dict
    # //// default only fired on a MISSING key: a contact with a blank full_name
    # //// printed an empty cell. `or _("Unknown")` covers both.
    if call.get("type") == "Incoming":
        call["activity_type"] = "incoming_call"
        contact = get_contact_by_phone_number(call.get("from"))
        receiver = (
            frappe.db.get_values(
                "User", call.get("receiver"), ["full_name", "user_image"]
            )[0]
            if call.get("receiver")
            else [None, None]
        )
        call["_caller"] = {
            "label": contact.get("full_name") or _("Unknown"),
            "image": contact.get("image"),
        }
        call["_receiver"] = {
            "label": receiver[0] or _("Unknown"),
            "image": receiver[1] or "",
        }
    elif call.get("type") == "Outgoing":
        call["activity_type"] = "outgoing_call"
        contact = get_contact_by_phone_number(call.get("to"))
        caller = (
            frappe.db.get_values(
                "User", call.get("caller"), ["full_name", "user_image"]
            )[0]
            if call.get("caller")
            else [None, None]
        )
        call["_caller"] = {
            "label": caller[0] or _("Unknown"),
            "image": caller[1] or "",
        }
        call["_receiver"] = {
            "label": contact.get("full_name") or _("Unknown"),
            "image": contact.get("image"),
        }

    return call


def parse_call_logs(calls):
    return [parse_call_log(call) for call in calls] if calls else []


def is_json_valid(json_string):
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False


def is_frappe_version(version: str, above: bool = False, below: bool = False):
    from frappe.pulse.utils import get_frappe_version

    current_version = get_frappe_version()
    major_version = int(current_version.split(".")[0])
    target_version = int(version.split(".")[0])

    if above:
        return major_version >= target_version
    if below:
        return major_version < target_version
    return major_version == target_version
