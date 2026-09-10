# Copyright (c) 2021, Frappe Technologies and Contributors
# See license.txt

# import frappe
import unittest


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


class TestHDArticle(unittest.TestCase):
    pass
