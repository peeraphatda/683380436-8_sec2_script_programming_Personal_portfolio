"""Offline unit tests (no real email/network needed). Run: python -m unittest discover tests"""
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.email_receiver import EmailReceiver
from src.email_sender import EmailSender
from src.sms_gateway import SMSGateway
from src.utils import ensure_directory_exists, get_env_variable


class TestUtils(unittest.TestCase):
    def test_get_env_variable_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                get_env_variable("DOES_NOT_EXIST")

    def test_get_env_variable_present(self):
        with patch.dict(os.environ, {"FOO": "bar"}):
            self.assertEqual(get_env_variable("FOO"), "bar")

    def test_ensure_directory_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "a", "b")
            ensure_directory_exists(target)
            self.assertTrue(os.path.isdir(target))


class TestEmailSender(unittest.TestCase):
    def setUp(self):
        self.sender = EmailSender("smtp.test", 587, "me@test.com", "pw")

    def test_build_plain_message(self):
        msg = self.sender.build_message("you@test.com", "Hi", "Body")
        self.assertEqual(msg["To"], "you@test.com")
        self.assertEqual(msg["Subject"], "Hi")
        self.assertEqual(len(msg.get_payload()), 1)

    def test_build_message_with_attachment(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-test")
        try:
            msg = self.sender.build_message("you@test.com", "Hi", "Body", attachment_path=f.name)
            self.assertEqual(len(msg.get_payload()), 2)
        finally:
            os.remove(f.name)

    def test_missing_attachment_still_builds(self):
        msg = self.sender.build_message("you@test.com", "Hi", "Body", attachment_path="nope.pdf")
        self.assertEqual(len(msg.get_payload()), 1)

    @patch("src.email_sender.smtplib.SMTP")
    def test_send_email_success(self, smtp_cls):
        server = smtp_cls.return_value
        self.assertTrue(self.sender.send_email("you@test.com", "Hi", "Body"))
        server.starttls.assert_called_once()
        server.login.assert_called_once_with("me@test.com", "pw")
        server.send_message.assert_called_once()
        server.quit.assert_called_once()

    @patch("src.email_sender.smtplib.SMTP")
    def test_send_email_auth_failure(self, smtp_cls):
        import smtplib
        smtp_cls.return_value.login.side_effect = smtplib.SMTPAuthenticationError(535, b"bad")
        self.assertFalse(self.sender.send_email("you@test.com", "Hi", "Body"))


class TestSMSGateway(unittest.TestCase):
    def setUp(self):
        self.sender = EmailSender("smtp.test", 587, "me@test.com", "pw")
        self.sms = SMSGateway(self.sender)

    def test_requires_email_sender(self):
        with self.assertRaises(TypeError):
            SMSGateway("not a sender")

    def test_gateway_address(self):
        self.assertEqual(self.sms.build_gateway_address("123-456-7890", "att"), "1234567890@txt.att.net")
        self.assertEqual(self.sms.build_gateway_address("1234567890", "VERIZON"), "1234567890@vtext.com")
        self.assertEqual(self.sms.build_gateway_address("a@b.com"), "a@b.com")
        self.assertIsNone(self.sms.build_gateway_address("1234567890", "unknown"))

    def test_send_sms_calls_sender(self):
        self.sender.send_email = MagicMock(return_value=True)
        self.assertTrue(self.sms.send_sms("1234567890", "hello", "att"))
        self.sender.send_email.assert_called_once_with("1234567890@txt.att.net", "", "hello")

    def test_send_sms_unknown_carrier(self):
        self.assertFalse(self.sms.send_sms("1234567890", "hello", "unknown"))


class TestEmailReceiver(unittest.TestCase):
    def test_decode_plain_and_encoded_header(self):
        self.assertEqual(EmailReceiver._decode_header_part("Hello"), "Hello")
        self.assertEqual(EmailReceiver._decode_header_part("=?UTF-8?B?U3ViamVjdA==?="), "Subject")
        self.assertEqual(EmailReceiver._decode_header_part(None), "")

    @patch("src.email_receiver.imaplib.IMAP4_SSL")
    def test_search_emails(self, imap_cls):
        imap = imap_cls.return_value
        imap.uid.return_value = ("OK", [b"1 2 3"])
        r = EmailReceiver("imap.test", "me@test.com", "pw")
        self.assertEqual(r.search_emails(from_sender="a@b.com"), [b"1", b"2", b"3"])
        imap.logout.assert_called_once()


if __name__ == "__main__":
    unittest.main()
