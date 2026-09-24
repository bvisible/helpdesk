# Copyright (c) 2021, Frappe Technologies and Contributors
# See license.txt
import frappe
from frappe.tests import IntegrationTestCase


# //// Neoffice — `HD Article.wiki_document` is a Link to `Wiki Document`, added by
# //// this fork for the knowledge-base mirror (see kb_wiki_mirror.py). The test
# //// runner walks a doctype's Link fields to build its test records, and
# //// `get_modules` throws `DoesNotExistError: DocType Wiki Document not found` when
# //// the wiki app is not on the bench -- BEFORE a single test runs, so the whole
# //// helpdesk suite dies rather than one test failing.
# ////
# //// That is the normal state of many benches: helpdesk does not require wiki, the
# //// field is read-only, and the mirror is off by default.
# ////
# //// MODULE level, not the TestCase: frappe reads it as
# //// `hasattr(test_module, "test_ignore")` (frappe/test_runner.py, get_dependencies),
# //// so an attribute on the class is simply never seen. And it is not transitive
# //// either, so it belongs to the module of the doctype that CARRIES the link.
test_ignore = ["Wiki Document"]


class TestHDArticleFeedback(IntegrationTestCase):
    def setUp(self):
        self.article = frappe.get_doc(
            {
                "doctype": "HD Article",
                "title": "Test Article",
                "status": "Published",
                "content": "<p>Test content</p>",
            }
        ).insert()

    def tearDown(self):
        frappe.db.delete("HD Article Feedback", {"article": self.article.name})
        frappe.delete_doc("HD Article", self.article.name, force=True)

    def get_counts(self):
        likes = frappe.db.count(
            "HD Article Feedback",
            filters={"article": self.article.name, "feedback": 1},
        )
        dislikes = frappe.db.count(
            "HD Article Feedback",
            filters={"article": self.article.name, "feedback": 2},
        )
        return likes, dislikes

    def test_like_increases_like_count(self):
        self.article.set_feedback(1)
        likes, dislikes = self.get_counts()
        self.assertEqual(likes, 1)
        self.assertEqual(dislikes, 0)

    def test_dislike_increases_dislike_count(self):
        self.article.set_feedback(2)
        likes, dislikes = self.get_counts()
        self.assertEqual(likes, 0)
        self.assertEqual(dislikes, 1)

    def test_like_then_dislike_updates_correctly(self):
        self.article.set_feedback(1)
        likes, dislikes = self.get_counts()
        self.assertEqual(likes, 1)
        self.assertEqual(dislikes, 0)

        # on switching to dislike, like count should reduce and dislike should increase hence set feedback to 2
        self.article.set_feedback(2)
        likes, dislikes = self.get_counts()
        self.assertEqual(likes, 0)
        self.assertEqual(dislikes, 1)

    def test_dislike_then_like_updates_correctly(self):
        self.article.set_feedback(2)
        likes, dislikes = self.get_counts()
        self.assertEqual(likes, 0)
        self.assertEqual(dislikes, 1)

        # switch to like, dislike should reduce and like should increase
        self.article.set_feedback(1)
        likes, dislikes = self.get_counts()
        self.assertEqual(likes, 1)
        self.assertEqual(dislikes, 0)

    def test_same_feedback_does_not_change_count(self):
        self.article.set_feedback(1)
        likes_before, _ = self.get_counts()

        self.article.set_feedback(1)
        likes_after, _ = self.get_counts()

        self.assertEqual(likes_before, likes_after)

    def test_feedback_creates_single_record(self):
        # multiple calls should not create multiple records
        self.article.set_feedback(1)
        self.article.set_feedback(2)
        self.article.set_feedback(1)

        total = frappe.db.count(
            "HD Article Feedback",
            filters={
                "article": self.article.name,
                "user": frappe.session.user,
            },
        )
        self.assertEqual(total, 1)
