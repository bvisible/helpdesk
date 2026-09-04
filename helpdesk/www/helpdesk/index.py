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


#//// Neoffice — contract note on upstream's `allow_guest=True`. Reviewed
#//// 2026-09-04 and deliberately KEPT, neither loosened nor tightened.
#////
#//// Guest access is load-bearing for the dev flow, not an oversight.
#//// desk/src/main.js awaits this call BEFORE app.mount(), and the router's
#//// beforeEach guard — the thing that sends a logged-out visitor to /login —
#//// only runs once the app is mounted. There is no login screen inside the
#//// SPA to fall back on. Refuse Guest here and a logged-out developer on the
#//// vite dev server gets a blank page with no way to sign in.
#////
#//// What it exposes is bounded, and THAT is the property to preserve:
#//// get_boot() returns the CALLER's own session (its own csrf_token, its own
#//// session_user) plus site-wide display settings (date/time format,
#//// setup_complete, is_fc_site, socketio_port, default route). Nothing that
#//// belongs to another user, no credential. Any key added to get_boot()
#//// becomes readable by an anonymous visitor of a developer_mode site — weigh
#//// it against that before adding one. On production the developer_mode gate
#//// below closes the door entirely (the flag is 0 across the fleet).
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
