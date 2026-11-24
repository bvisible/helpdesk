import frappe


# //// Neoffice — the reason our CI asks of a public method.
@frappe.whitelist(allow_guest=True)  # nosemgrep
def get_config():  # permission-check: ok the brand and display settings a visitor's page needs, upstream's
    fields = [
        "brand_name",
        "brand_logo",
        "favicon",
        "prefer_knowledge_base",
        "setup_complete",
        "skip_email_workflow",
        "is_feedback_mandatory",
        "restrict_tickets_by_agent_group",
        "assign_within_team",
        "disable_saved_replies_global_scope",
        "enable_comment_reactions",
    ]
    res = frappe.get_value(doctype="HD Settings", fieldname=fields, as_dict=True)

    # //// Neoffice — upstream's mark is no longer the last resort: without a favicon of the site, the page keeps the
    # //// icons it came with, ours (desk/src/App.vue, neoffice_theme/home_screen.py).
    res.favicon = res.favicon or frappe.db.get_single_value(
        "Website Settings", "favicon"
    )
    return res
