# //// Neoffice — added file (no upstream equivalent).
"""A busy corpus lock is not a failure of whoever finds it taken.

download_corpus runs from after_migrate and from every scheduler tick behind a
bench-wide one-second lock. A migrate that met a tick exited 1 after doing all
its work. The lock being held means the same idempotent download is already
happening: the caller must return, not raise.
"""

import unittest
from unittest import mock

from frappe.utils.file_lock import LockTimeoutError

from helpdesk import search


class TestCorpusLock(unittest.TestCase):
    def test_a_held_lock_is_not_an_error(self):
        with mock.patch.object(search, "_download_corpus", side_effect=LockTimeoutError("held")):
            self.assertIsNone(search.download_corpus())

    def test_a_real_failure_still_surfaces(self):
        with mock.patch.object(search, "_download_corpus", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                search.download_corpus()

    def test_the_download_itself_still_runs(self):
        with mock.patch.object(search, "_download_corpus") as download:
            search.download_corpus()
        download.assert_called_once_with()
