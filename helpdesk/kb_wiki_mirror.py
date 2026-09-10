# //// Neoffice — added file (no upstream equivalent).
# ////
# //// Upstream keeps two knowledge bases that ignore each other: `HD Article` here,
# //// and the wiki app next door. `grep -ri wiki` over the whole helpdesk repo returns
# //// nothing. So an instance running both ends up writing the same answer twice, or
# //// — what actually happens — writing it once and losing it.
# ////
# //// This mirrors them, ONE WIKI SPACE ONLY, and that bound is the feature, not an
# //// implementation detail. The wiki also carries company knowledge (NORA writes into
# //// it), while a helpdesk article is PUBLIC on the customer portal. A "sync the whole
# //// wiki" mirror would publish internal pages to customers. So: a dedicated space is
# //// created for the knowledge base, only its documents are mirrored, and every other
# //// space is invisible to the helpdesk.
# ////
# //// On the wiki side the live tree IS the `Wiki Document` records — that is what
# //// wiki_revision.create_revision_from_live_tree() reads to build a revision. Writing
# //// a Wiki Document is therefore the normal way to edit, not a way around the
# //// versioning; the revision is refreshed afterwards so change requests stay aligned.
# ////
# //// Content formats differ and only one direction is lossless: HD Article holds HTML
# //// (Text Editor), Wiki Document holds Markdown. Markdown accepts raw HTML, so
# //// article -> wiki passes the HTML through untouched; wiki -> article runs
# //// frappe.utils.md_to_html. No round trip loses content.
# ////
# //// Which is exactly why the two sides CANNOT be compared to each other to decide
# //// whether something changed. After one wiki edit the article holds
# //// `<p>Open <strong>Settings</strong></p>` while the wiki holds
# //// `Open **Settings**` — the same text in two formats. A first version compared the
# //// raw contents, concluded "they differ", and overwrote the author's Markdown with
# //// generated HTML on the next save of the article. Caught by the test that saves an
# //// UNCHANGED article and asserts the wiki document was not touched.
# ////
# //// So each side is compared to ITSELF as of the last sync: `wiki_sync_hashes` on the
# //// article keeps a fingerprint of both contents at that moment. Unchanged on a side
# //// means nothing to push from it.

import hashlib
import json

import frappe
from frappe import _
from frappe.utils import md_to_html


def _fingerprint(text):
    return hashlib.sha1((text or "").encode("utf-8")).hexdigest()


def _sync_state(article_name):
    raw = frappe.db.get_value("HD Article", article_name, "wiki_sync_hashes")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except ValueError:
        return {}


def _remember(article_name, html, markdown):
    frappe.db.set_value(
        "HD Article",
        article_name,
        "wiki_sync_hashes",
        json.dumps({"hd": _fingerprint(html), "wiki": _fingerprint(markdown)}),
        update_modified=False,
    )

# route of the dedicated space; the DISPLAYED name is translated at creation
KB_SPACE_ROUTE = "knowledge-base"


def wiki_installed():
    return "wiki" in frappe.get_installed_apps()


def mirror_enabled():
    """Off unless someone turned it on. A mirror that starts by itself would publish
    articles into a space nobody asked for."""
    if not wiki_installed():
        return False
    return bool(frappe.db.get_single_value("HD Settings", "mirror_kb_to_wiki"))


def get_kb_space(create=False):
    """The one Wiki Space the knowledge base mirrors into.

    Stored on HD Settings rather than looked up by route: a route can be renamed
    by a wiki admin, and the mirror must not silently start writing into whatever
    space happens to answer to `knowledge-base` afterwards.
    """
    space = frappe.db.get_single_value("HD Settings", "kb_wiki_space")
    if space and frappe.db.exists("Wiki Space", space):
        return space
    if not create:
        return None

    doc = frappe.new_doc("Wiki Space")
    doc.route = KB_SPACE_ROUTE
    # named for the reader, not for the app it came from
    doc.space_name = _("Knowledge Base")
    doc.public_read = 1
    doc.is_published = 1
    doc.flags.ignore_permissions = True
    doc.insert(ignore_permissions=True)  # before_insert creates the root group
    frappe.db.set_single_value("HD Settings", "kb_wiki_space", doc.name)
    return doc.name


def _category_group(space, category):
    """The Wiki Document group standing for an HD Article Category.

    Categories are a flat list here and a tree there; one level is enough and
    keeps the mirror reversible.
    """
    if not category:
        return frappe.db.get_value("Wiki Space", space, "root_group")

    root = frappe.db.get_value("Wiki Space", space, "root_group")
    title = frappe.db.get_value("HD Article Category", category, "category_name") or category
    existing = frappe.db.get_value(
        "Wiki Document",
        {"parent_wiki_document": root, "is_group": 1, "title": title},
        "name",
    )
    if existing:
        return existing

    group = frappe.new_doc("Wiki Document")
    group.title = title
    group.is_group = 1
    group.is_published = 1
    group.parent_wiki_document = root
    group.wiki_space = space
    group.flags.ignore_permissions = True
    group.insert(ignore_permissions=True)
    return group.name


def _refresh_revision(space):
    """Realign the space's main revision on the live tree.

    Same call the wiki makes after a direct reorder — without it, a change request
    opened later would diff against a revision that predates the mirror's writes.
    Best effort: a revision that fails to build must not roll back the article the
    user just saved.
    """
    try:
        from wiki.api.wiki_space import _sync_main_revision_for_space

        _sync_main_revision_for_space(space)
    except Exception:
        frappe.log_error(
            "KB mirror could not refresh the wiki revision",
            f"Wiki Space: {space}\n\n{frappe.get_traceback()}",
        )


def article_to_wiki(doc, method=None):
    """HD Article -> Wiki Document, inside the dedicated space."""
    if doc.flags.get("from_wiki_mirror") or not mirror_enabled():
        return

    space = get_kb_space(create=True)
    if not space:
        return

    content = doc.content or ""
    published = 1 if doc.status == "Published" else 0
    target = doc.get("wiki_document")

    if target and frappe.db.exists("Wiki Document", target):
        current = frappe.db.get_value(
            "Wiki Document", target, ["title", "content", "is_published"], as_dict=True
        )
        state = _sync_state(doc.name)
        # The article is compared to ITSELF as of the last sync, never to the wiki
        # side: the two hold the same text in different formats, so comparing them
        # always says "changed" and would overwrite the author's Markdown with
        # generated HTML. Title and published flag are the same on both sides, so
        # those can be compared directly.
        unchanged_here = state.get("hd") == _fingerprint(content)
        if (
            unchanged_here
            and current.title == doc.title
            and int(current.is_published or 0) == published
        ):
            return
        wiki_doc = frappe.get_doc("Wiki Document", target)
    else:
        wiki_doc = frappe.new_doc("Wiki Document")
        wiki_doc.wiki_space = space
        wiki_doc.parent_wiki_document = _category_group(space, doc.category)

    wiki_doc.title = doc.title
    wiki_doc.content = content
    wiki_doc.is_published = published
    wiki_doc.flags.from_kb_mirror = True
    wiki_doc.flags.ignore_permissions = True
    wiki_doc.save(ignore_permissions=True)

    if doc.get("wiki_document") != wiki_doc.name:
        frappe.db.set_value("HD Article", doc.name, "wiki_document", wiki_doc.name, update_modified=False)

    # both sides are identical right now: remember it, so neither hook sees a change
    _remember(doc.name, content, content)
    _refresh_revision(space)


def wiki_to_article(doc, method=None):
    """Wiki Document -> HD Article, and only from the dedicated space."""
    if doc.flags.get("from_kb_mirror") or not mirror_enabled():
        return
    if doc.get("is_group"):
        return

    space = get_kb_space()
    # THE bound: any other space is company knowledge and never reaches the portal
    if not space or doc.get("wiki_space") != space:
        return

    article = frappe.db.get_value("HD Article", {"wiki_document": doc.name}, "name")
    html = md_to_html(doc.content or "") or ""
    status = "Published" if doc.get("is_published") else "Draft"

    if article:
        current = frappe.db.get_value("HD Article", article, ["title", "content", "status"], as_dict=True)
        state = _sync_state(article)
        unchanged_here = state.get("wiki") == _fingerprint(doc.content or "")
        if unchanged_here and current.title == doc.title and current.status == status:
            return
        hd = frappe.get_doc("HD Article", article)
    else:
        hd = frappe.new_doc("HD Article")
        hd.category = _default_category()
        hd.wiki_document = doc.name
        hd.author = frappe.session.user

    hd.title = doc.title
    hd.content = html
    hd.status = status
    hd.flags.from_wiki_mirror = True
    hd.flags.ignore_permissions = True
    hd.save(ignore_permissions=True)

    # the article now holds the HTML rendering of this Markdown: record both, so a
    # later save of either side knows nothing moved
    _remember(hd.name, html, doc.content or "")


def _default_category():
    """Where a wiki-born article lands. HD Article requires a category."""
    existing = frappe.db.get_value("HD Article Category", {}, "name")
    if existing:
        return existing
    category = frappe.new_doc("HD Article Category")
    category.category_name = _("General")
    category.flags.ignore_permissions = True
    category.insert(ignore_permissions=True)
    return category.name


@frappe.whitelist()
def backfill():
    """Push every existing article into the wiki once.

    Called by hand from HD Settings, never on its own: turning the mirror on is a
    decision, and so is publishing the whole existing knowledge base into a space.
    """
    if not frappe.has_permission("HD Settings", "write"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    if not mirror_enabled():
        frappe.throw(_("Enable the wiki mirror in HD Settings first"))

    done = 0
    for row in frappe.get_all("HD Article", fields=["name"]):
        try:
            article_to_wiki(frappe.get_doc("HD Article", row.name))
            done += 1
        except Exception:
            frappe.log_error(
                "KB mirror skipped an article",
                f"HD Article: {row.name}\n\n{frappe.get_traceback()}",
            )
    frappe.db.commit()
    return {"mirrored": done}
