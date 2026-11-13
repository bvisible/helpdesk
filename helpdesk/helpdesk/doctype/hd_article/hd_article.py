# Copyright (c) 2021, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

from helpdesk.utils import capture_event


class HDArticle(Document):
    def validate(self):
        self.validate_article_category()
        self.validate_published_content()

    def validate_article_category(self):
        if self.has_value_changed("category") and not self.is_new():
            old_category = self.get_doc_before_save().get("category")
            self.check_category_length(old_category)

    def validate_published_content(self):
        if self.status == "Published" and not self.content:
            frappe.throw(_("Published articles must have content."))

    def before_insert(self):
        self.author = frappe.session.user

    def before_save(self):
        # set published date of the hd_article
        if self.status == "Published" and not self.published_on:
            self.published_on = frappe.utils.now()
        elif self.status == "Draft" and self.published_on:
            self.published_on = None

        if self.status == "Archived" and self.category != None:
            self.category = None

        # index is only set if its not set already, this allows defining index
        # at the time of creation itself if not set the index is set to the
        # last index + 1, i.e. the hd_article is added at the end
        if self.status == "Published" and self.idx == -1:
            self.idx = cint(
                frappe.db.count(
                    "HD Article",
                    {"category": self.category, "status": "Published"},
                )
            )

    def after_insert(self):
        count = frappe.db.count("HD Article")
        if count == 1:
            return
        capture_event("article_created")

    def on_trash(self):
        self.check_category_length()

    def check_category_length(self, category=None):
        category = category or self.get("category")
        if not category:
            return
        category_articles = frappe.db.count("HD Article", {"category": category})
        if category_articles == 1:
            frappe.throw(_("Category must have atleast one article"))

    @staticmethod
    def default_list_data():
        # //// Neoffice ▼▼▼ — every column label below wrapped in _() so the
        # //// French catalogue can translate it: default_list_data() is called
        # //// per request, so _() resolves in the caller's own language
        # //// (97629bb44 "fix(i18n): the list columns, sort options and
        # //// filters could not be translated at all").
        columns = [
            {
                "label": _("Title"),
                "type": "Data",
                "key": "title",
                "width": "20rem",
            },
            {
                # //// Neoffice — see the block marker above: __() i18n wrap
                "label": _("Status"),
                "type": "status",
                "key": "status",
                "width": "10rem",
            },
            {
                # //// Neoffice — see the block marker above: __() i18n wrap
                "label": _("Author"),
                "type": "Link",
                "key": "author",
                "width": "17rem",
            },
            {
                # //// Neoffice — see the block marker above: __() i18n wrap
                "label": _("Last Modified"),
                "type": "Datetime",
                "key": "modified",
                "width": "8rem",
            },
        ]
        # //// Neoffice ▲▲▲
        return {"columns": columns}

    @frappe.whitelist()
    def set_feedback(self, value: int):
        # 0 empty, 1 like, 2 dislike
        user = frappe.session.user
        # //// Neoffice — this method is the only door to HD Article Feedback (neoffice-maintenance#531). Upstream
        # inserts the vote under the caller's own rights, so the sites carried a Custom DocPerm opening the doctype to
        # `All`: every portal account could then rewrite or delete anyone's vote straight through the REST collection.
        # neoffice_custom_fields' reclose_frozen_open_grants now realigns the doctype on what helpdesk ships (HD Customer,
        # owner only); the vote is inserted here instead, after run_doc_method checked the caller may read the article.
        # Guest is refused: one shared "Guest" vote per article is no vote. Keep this block through an upstream merge.
        if user == "Guest":
            frappe.throw(
                _("Please log in to rate this article."), frappe.PermissionError
            )
        value = cint(value)
        if value not in (0, 1, 2):
            frappe.throw(_("Invalid feedback value."))
        # //// Neoffice ▲▲▲

        feedback = frappe.db.exists(
            "HD Article Feedback", {"user": user, "article": self.name}
        )
        if feedback:
            current_value = frappe.db.get_value(
                "HD Article Feedback", feedback, "feedback"
            )
            if int(current_value) == value:
                return
            frappe.db.set_value("HD Article Feedback", feedback, "feedback", value)
            frappe.db.set_value("HD Article Feedback", feedback, "feedback", value)
        else:
            frappe.new_doc(
                "HD Article Feedback", user=user, article=self.name, feedback=value
            ).insert(
                ignore_permissions=True
            )  # //// Neoffice — the method is the gate (#531), see above

    @property
    def title_slug(self) -> str:
        """
        Generate slug from article title.
        Example: "Introduction to Frappe Helpdesk" -> "introduction-to-frappe-helpdesk"

        :return: Generated slug
        """
        return self.title.lower().replace(" ", "-")
