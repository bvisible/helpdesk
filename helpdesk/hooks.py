app_name = "helpdesk"
app_title = "Helpdesk"
app_publisher = "Frappe Technologies"
app_description = "Customer Service Software"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "hello@frappe.io"
app_license = "AGPLv3"
required_apps = ["telephony"]
require_type_annotated_api_methods = True

add_to_apps_screen = [
    {
        "name": "helpdesk",
        "logo": "/assets/helpdesk/desk/favicon.svg",
        "title": "Helpdesk",
        "route": "/helpdesk",
        "has_permission": "helpdesk.api.permission.has_app_permission",
    }
]

get_site_info = "helpdesk.activation.get_site_info"

after_install = "helpdesk.setup.install.after_install"
after_migrate = [
    "helpdesk.search.build_index_in_background",
    "helpdesk.search.download_corpus",
]

# Full Text Search
# ------------------

sqlite_search = ["helpdesk.search_sqlite.HelpdeskSearch"]

scheduler_events = {
    "all": [
        "helpdesk.search.build_index_if_not_exists",
        "helpdesk.search.download_corpus",
    ],
    "daily": [
        "helpdesk.helpdesk.doctype.hd_ticket.hd_ticket.close_tickets_after_n_days"
    ],
    "hourly_long": [
        "helpdesk.helpdesk.doctype.hd_ticket.hd_ticket.update_sla_status_in_ticket"
    ],
}


website_route_rules = [
    {
        "from_route": "/helpdesk/<path:app_path>",
        "to_route": "helpdesk",
    },
]

user_invitation = {
    "allowed_roles": {
        "Agent Manager": [
            "Agent",
            "Agent Manager",
            "HD Customer",
            "HD Customer Manager",
        ],
        "System Manager": [
            "Agent",
            "Agent Manager",
            "System Manager",
            "HD Customer",
            "HD Customer Manager",
        ],
    },
    "after_accept": "helpdesk.helpdesk.hooks.user_invitation.after_accept",
    "extra_invite_params": ["customer", "contact"],
}

doc_events = {
    # //// Neoffice — the knowledge base and the wiki used to ignore each other
    # //// entirely (grep -ri wiki over this repo returned nothing), so the same
    # //// answer got written twice or lost. Mirrored both ways, but inside ONE
    # //// dedicated wiki space: the wiki also holds company knowledge, and a
    # //// helpdesk article is public on the customer portal. Off by default.
    # //// See kb_wiki_mirror.py.
    "HD Article": {
        "on_update": "helpdesk.kb_wiki_mirror.article_to_wiki",
    },
    "Wiki Document": {
        "on_update": "helpdesk.kb_wiki_mirror.wiki_to_article",
    },
    # //// Neoffice — a Contact is nearly always attached to its Customer AFTER being
    # //// created, so this runs on update (insert included). Upstream v1.31.0 dropped its
    # //// own Contact hook; membership is now a child table of HD Customer, which
    # //// overrides/customer.py fills from the ERP link. See link_contact_to_hd_customer.
    "Contact": {
        "on_update": "helpdesk.overrides.customer.link_contact_to_hd_customer",
    },
    "Assignment Rule": {
        "on_trash": "helpdesk.extends.assignment_rule.on_assignment_rule_trash",
        "validate": "helpdesk.extends.assignment_rule.on_assignment_rule_validate",
    },
    "Customer": {
        # //// Neoffice — HD Customer mirrors ERPNext's Customer; without this the
        # //// helpdesk Customers screen is empty on an instance that runs both, and the
        # //// portal shows a contact only the tickets they raised themselves (the
        # //// permission query filters on customer). Upstream's two-way integration
        # //// (off unless ERPNext HD Settings is enabled) is listed first and wins when
        # //// on: our handler steps aside then. See overrides/customer.py.
        "after_insert": [
            "helpdesk.integrations.erpnext.customer.after_insert",
            "helpdesk.overrides.customer.sync_to_hd_customer",
        ],
        "on_update": [
            "helpdesk.integrations.erpnext.customer.on_update",
            "helpdesk.overrides.customer.sync_to_hd_customer",
        ],
        "before_rename": "helpdesk.integrations.erpnext.customer.before_rename",
        "after_rename": "helpdesk.integrations.erpnext.customer.after_rename",
        "on_trash": "helpdesk.integrations.erpnext.customer.on_trash",
    },
    "User Permission": {
        "before_validate": "helpdesk.integrations.erpnext.user_permission.before_validate",
        "after_insert": "helpdesk.integrations.erpnext.user_permission.after_insert",
        "on_update": "helpdesk.integrations.erpnext.user_permission.on_update",
        "on_trash": "helpdesk.integrations.erpnext.user_permission.on_trash",
    },
    "DocShare": {
        "before_validate": "helpdesk.integrations.erpnext.doc_share.before_validate",
        "after_insert": "helpdesk.integrations.erpnext.doc_share.after_insert",
        "on_update": "helpdesk.integrations.erpnext.doc_share.on_update",
        "on_trash": "helpdesk.integrations.erpnext.doc_share.on_trash",
    },
    "Notification Log": {
        "before_insert": "helpdesk.extends.notification_log.before_insert",
    },
    "Comment": {
        "before_insert": "helpdesk.extends.comment.before_insert",
        "validate": "helpdesk.extends.comment.validate",
        "on_trash": "helpdesk.extends.comment.on_trash",
    },
}

# For List View
permission_query_conditions = {
    "HD Ticket": "helpdesk.helpdesk.doctype.hd_ticket.hd_ticket.permission_query",
    "HD Saved Reply": "helpdesk.helpdesk.doctype.hd_saved_reply.hd_saved_reply.permission_query",
    "HD Customer": "helpdesk.helpdesk.doctype.hd_customer.hd_customer.permission_query",
}


has_permission = {
    "HD Agent": "helpdesk.helpdesk.doctype.hd_agent.hd_agent.has_permission",
    "HD Ticket": "helpdesk.helpdesk.doctype.hd_ticket.hd_ticket.has_permission",
    "HD Saved Reply": "helpdesk.helpdesk.doctype.hd_saved_reply.hd_saved_reply.has_permission",
    "HD Customer": "helpdesk.helpdesk.doctype.hd_customer.hd_customer.has_permission",
    "Comment": "helpdesk.extends.comment.has_permission",
}

override_whitelisted_methods = {
    "frappe.realtime.has_permission": "helpdesk.overrides.realtime.has_permission",
    "frappe.realtime.can_subscribe_doc": "helpdesk.overrides.realtime.can_subscribe_doc",
}


notification_skip_email_types = [
    "Reaction",
    "Ticket Reopened",
]


# DocType Class
# ---------------
# Override standard doctype classes
override_doctype_class = {
    "Email Account": "helpdesk.overrides.email_account.CustomEmailAccount",
    "Assignment Rule": "helpdesk.overrides.assignment_rule.HelpdeskAssignmentRule",
    "User Invitation": "helpdesk.overrides.user_invitation.HelpdeskUserInvitation",
}

ignore_links_on_delete = [
    "HD Notification",
    "HD Ticket Comment",
]

# setup wizard
# setup_wizard_requires = "assets/helpdesk/js/setup_wizard.js"
# setup_wizard_stages = "helpdesk.setup.setup_wizard.get_setup_stages"
setup_wizard_complete = "helpdesk.setup.setup_wizard.setup_complete"


# Testing
# ---------------

before_tests = "helpdesk.test_utils.before_tests"
auth_hooks = ["helpdesk.auth.authenticate"]
