import datetime
import sys
from unittest.mock import call, MagicMock

import pytest

smtp_module_mock = MagicMock()
smtp_SMTP_mock = MagicMock()
smtp_module_mock.SMTP = smtp_SMTP_mock
sys.modules['smtplib'] = smtp_module_mock
from ipa_notify.notifier import Notifier


@pytest.fixture
def notifier():
	return Notifier("localhost", 25, "user", "pwd", "noreply@test.com")


def test_send_email(notifier):
	notifier._send_email("user@test.com", "Subject", "Body")
	call1 = call().login("user", "pwd")
	call2 = call().quit()
	smtp_SMTP_mock.assert_has_calls([call1])
	smtp_SMTP_mock.assert_has_calls([call2])


def test_notify_expiration(notifier):
	notifier._send_email = MagicMock()
	current_date = datetime.datetime.now()
	notifier.notify_expiration("user@test.com", current_date, 5)

	notifier._send_email.assert_called_with(
		"user@test.com", f"Password will expire in 5 days",
		f"Your password will expire on {current_date}"
	)

	notifier._send_email = MagicMock()
	current_date = datetime.datetime.now()
	notifier.notify_expiration("user@test.com", current_date, -5)

	notifier._send_email.assert_called_with(
		"user@test.com", "Your password expired",
		f"Your password expired on {current_date}"
	)


def test_notify_locked_user(notifier):
	notifier._send_email = MagicMock()
	locked_users = {
		"user1": ["server1"],
		"user2": ["server1", "server2"]
	}
	notifier.notify_locked_users("user@test.com", locked_users)
	notifier._send_email.assert_called_with(
		"user@test.com", "Locked Users",
		"Following users are locked\nuser1 blocked on server1\nuser2 blocked on server1, server2"
	)
