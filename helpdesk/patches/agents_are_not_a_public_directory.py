# //// Neoffice — added file (no upstream equivalent).
# ////
# //// THE AGENT LIST WAS ENUMERABLE BY ANY PORTAL ACCOUNT.
# ////
# //// `HD Agent` granted `select` to the role `All` — and `select` is NOT
# //// `read`: it exists so somebody can pick a value in a Link field without
# //// being able to open the document. On most doctypes that distinction is
# //// exactly right. Here it is not, because an agent's NAME is their e-mail
# //// address: the right to pick one from a list IS the right to know every
# //// agent's address.
# ////
# //// Measured on a dev instance with a real portal session, over HTTP:
# //// `has_permission(read)` answered False and the document was refused —
# //// and the collection endpoint still returned every agent's address. A
# //// permission audit that only reads `read` sees nothing here.
# ////
# //// Removing the flag from the doctype JSON is not enough on a site that
# //// already exists: once any `Custom DocPerm` exists for a doctype, those
# //// rows REPLACE the ones the code ships, so a file-only fix would look
# //// applied and change nothing.

import frappe


def execute():
	if not frappe.db.exists("DocType", "HD Agent"):
		return

	#: `select` only. What `All` may otherwise do here (email, print, share,
	#: export, report) is inert without `read`, and a patch that quietly
	#: widened its own scope would be the harder one to review.
	for table in ("Custom DocPerm", "DocPerm"):
		rows = frappe.get_all(
			table, filters={"parent": "HD Agent", "role": "All", "select": 1}, pluck="name"
		)
		if not rows:
			continue
		for name in rows:
			frappe.db.set_value(table, name, "select", 0, update_modified=False)
		print(f"agents_are_not_a_public_directory: cleared select on {len(rows)} {table} row(s)")

	frappe.clear_cache(doctype="HD Agent")
