# //// Neoffice — added file (no upstream equivalent).
"""A mail server that does not answer is not a folder error.

get_incoming_server(in_receive=True) swallows a timeout or a refused login and
returns an EmailServer that never got its `imap`. The pull then crashed on
select_imap_folder and logged "'EmailServer' object has no attribute 'imap'"
every 2 minutes of a provider outage (11 times on 2026-09-23). The framework
already counts the failure and disables the account past six in a row: the
pull must simply stop.
"""

import unittest
from unittest import mock

from frappe import _dict

from helpdesk.overrides.email_account import CustomEmailAccount


class _ServerWithoutConnection:
    """What get_incoming_server returns when connect() failed: no imap, no pop."""


def _account(use_imap=1):
    account = CustomEmailAccount.__new__(CustomEmailAccount)
    account.__dict__.update(
        {
            "name": "Support Test",
            "enable_incoming": 1,
            "use_imap": use_imap,
            "service": "",
            "email_sync_option": "ALL",
            "imap_folder": [_dict(folder_name="INBOX", append_to="HD Ticket", uidvalidity="1")],
        }
    )
    return account


class TestConnectionFailure(unittest.TestCase):
    def _pull(self, account, server):
        with (
            mock.patch.object(CustomEmailAccount, "build_email_sync_rule", return_value="UID 1:*"),
            mock.patch.object(CustomEmailAccount, "get_incoming_server", return_value=server),
            mock.patch.object(CustomEmailAccount, "log_error") as log_error,
        ):
            mails = account.get_inbound_mails()
        return mails, log_error

    def test_a_failed_imap_connection_returns_quietly(self):
        mails, log_error = self._pull(_account(use_imap=1), _ServerWithoutConnection())
        self.assertEqual(mails, [])
        log_error.assert_not_called()

    def test_a_failed_pop_connection_returns_quietly(self):
        mails, log_error = self._pull(_account(use_imap=0), _ServerWithoutConnection())
        self.assertEqual(mails, [])
        log_error.assert_not_called()

    def test_no_server_at_all_returns_quietly(self):
        mails, log_error = self._pull(_account(), None)
        self.assertEqual(mails, [])
        log_error.assert_not_called()

    def test_a_connected_server_is_still_read(self):
        server = mock.Mock()
        server.settings = {}
        server.select_imap_folder.return_value = True
        server.get_messages.return_value = {"latest_messages": []}
        mails, log_error = self._pull(_account(), server)
        self.assertEqual(mails, [])
        server.get_messages.assert_called_once()
        server.logout.assert_called_once()
        log_error.assert_not_called()


if __name__ == "__main__":
    unittest.main()
