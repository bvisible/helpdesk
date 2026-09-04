import frappe
from frappe import _
from frappe.integrations.frappe_providers.frappecloud_billing import is_fc_site
from frappe.utils import cint
from frappe.utils.telemetry import capture

no_cache = 1


def get_context(context):
    frappe.db.commit()
    context.boot = get_boot()

    # telemetry
    if frappe.session.user != "Guest":
        capture("active_site", "helpdesk")
    return context


@frappe.whitelist(methods=["POST"], allow_guest=True)
def get_context_for_dev():
    if not frappe.conf.developer_mode:
        frappe.throw(_("This method is only meant for developer mode"))
    return get_boot()


def get_boot():
    return frappe._dict(
        {
            "default_route": get_default_route(),
            "site_name": frappe.local.site,
            "read_only_mode": frappe.flags.read_only,
            "csrf_token": frappe.sessions.get_csrf_token(),
            "setup_complete": cint(frappe.get_system_settings("setup_complete")),
            "is_fc_site": is_fc_site(),
            "session_user": frappe.session.user,
            "date_format": frappe.get_system_settings("date_format"),
            "time_format": frappe.get_system_settings("time_format"),
            #//// Neoffice — added key. desk/src/socket.ts resolves the socket.io
            #//// port from `window.socketio_port`, and NOTHING in this repo ever
            #//// set it, so its hard-coded "9000" fallback was the only value in
            #//// play — wrong on any bench whose socketio_port differs, and
            #//// invisible in production only because window.location.port is
            #//// empty behind nginx, which drops the port from the URL entirely.
            #//// This dict is the injection itself: every key here is emitted as
            #//// `window["<key>"]` into the served page, AND re-read from
            #//// get_context_for_dev() onto `window` by desk/src/main.js in dev,
            #//// so one key honours the contract on both paths. Note that the
            #//// `window.site_name = "{{ site_name }}"` line in desk/index.html
            #//// is NOT that mechanism and never was: `site_name` is not in the
            #//// website context, so Jinja leaves the placeholder literal in the
            #//// page — it only works because this dict overwrites it further
            #//// down. Not sensitive: frappe's own desk boot ships the same
            #//// port to every logged-in and guest page.
            "socketio_port": frappe.conf.socketio_port or 9000,
        }
    )


def get_default_route():
    return "/helpdesk"
