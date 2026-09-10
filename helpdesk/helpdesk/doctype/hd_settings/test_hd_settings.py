# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt
from __future__ import unicode_literals

import unittest

# //// Neoffice — `HD Settings.kb_wiki_space` is a Link to `Wiki Space`, added by
# //// this fork to name the one wiki space the knowledge base mirrors into (see
# //// kb_wiki_mirror.py). The test runner walks a doctype's Link fields to build
# //// its test records and throws `DoesNotExistError: DocType Wiki Space not
# //// found` on a bench without the wiki app -- before the first test, killing the
# //// whole suite. Same reason and same shape as `Wiki Document` on HD Article.
# ////
# //// These two are the ONLY links helpdesk has into a doctype the bench may not
# //// carry: checked by listing every Link/Table `options` of every helpdesk
# //// doctype against what frappe + erpnext + telephony + helpdesk provide.
# ////
# //// MODULE level, not the TestCase: frappe reads it as
# //// `hasattr(test_module, "test_ignore")` (frappe/test_runner.py).
test_ignore = ["Wiki Space"]


class TestHDSettings(unittest.TestCase):
    pass
