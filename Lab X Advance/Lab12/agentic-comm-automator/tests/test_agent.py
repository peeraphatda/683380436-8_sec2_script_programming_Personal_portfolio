"""Offline unit tests (mocked mail/SMS). Run: python -m unittest discover tests"""
import json
import os
import sys
import tempfile
import unittest
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from unittest.mock import MagicMock, patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.communication_agent import CommunicationAgent
from src.config_parser import ConfigParser, expand_env
from src.email_tasks import EmailTasks
from src.sms_tasks import SMSTasks
from src.template_renderer import TemplateRenderer


class TestTemplateRenderer(unittest.TestCase):
    def test_render_and_format_spec(self):
        r = TemplateRenderer()
        self.assertEqual(r.render("Total ${v:.2f} on {d}", {"v": 12.5, "d": "today"}), "Total $12.50 on today")

    def test_missing_key_raises(self):
        with self.assertRaises(ValueError):
            TemplateRenderer().render("Hi {nope}", {})


class TestConfig(unittest.TestCase):
    def test_env_expansion_keeps_template_fields(self):
        with patch.dict(os.environ, {"MY_VAR": "x@y.com"}):
            out = expand_env({"a": ["${MY_VAR}"], "b": "${sales:.2f}"})
        self.assertEqual(out["a"], ["x@y.com"])
        self.assertEqual(out["b"], "${sales:.2f}")

    def test_missing_env_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                expand_env("${NOT_SET_ANYWHERE}")

    def test_validation_errors(self):
        bad = [
            {},
            {"tasks": []},
            {"tasks": [{"type": "send_email"}]},
            {"tasks": [{"type": "fax", "name": "x", "parameters": {}}]},
            {"tasks": [{"type": "send_email", "name": "x", "parameters": {"recipients": {"to": []},
                        "subject_template": "s", "body_template": "b"}}]},
            {"tasks": [{"type": "send_sms", "name": "x", "parameters": {"phone_numbers": ["1"]}}]},
            {"tasks": [{"type": "process_inbox", "name": "x", "parameters": {
                "search_criteria": {}, "rules": [{"if": {}, "then": {"explode": True}}]}}]},
        ]
        for cfg in bad:
            with self.assertRaises(ValueError, msg=str(cfg)):
                ConfigParser.validate(cfg)

    def test_shipped_config_is_valid(self):
        env = {k: "a@b.com" for k in ("SENDER_EMAIL", "TEST_RECIPIENT_EMAIL")}
        env.update({"TEST_SMS_PHONE_NUMBER": "1234567890", "TEST_SMS_CARRIER": "att",
                    "STUDENT_NAME": "Test User", "STUDENT_ID": "123"})
        with patch.dict(os.environ, env):
            cfg = ConfigParser(os.path.join(ROOT, "configs", "comm_pipeline_config.json")).load_config()
        self.assertEqual(len(cfg["tasks"]), 4)
        self.assertEqual(cfg["tasks"][0]["parameters"]["recipients"]["to"], ["a@b.com"])


def _raw_email(subject="Data Request - Urgent", body="This is urgent", attach=True):
    msg = MIMEMultipart()
    msg["From"] = "Me <me@test.com>"
    msg["To"] = "me@test.com"
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    if attach:
        part = MIMEApplication(b"%PDF-data", Name="r.pdf")
        part["Content-Disposition"] = 'attachment; filename="../r.pdf"'
        msg.attach(part)
    return msg.as_bytes()


class TestEmailTasks(unittest.TestCase):
    def setUp(self):
        self.et = EmailTasks("smtp.t", 587, "imap.t", "me@test.com", "pw")

    @patch("src.email_tasks.smtplib.SMTP")
    def test_send_email_includes_bcc_only_in_envelope(self, smtp_cls):
        server = smtp_cls.return_value.__enter__.return_value
        ok = self.et.send_email({"to": ["a@x.com"], "cc": ["c@x.com"], "bcc": ["b@x.com"]}, "S", "B")
        self.assertTrue(ok)
        msg = server.send_message.call_args[0][0]
        self.assertNotIn("b@x.com", msg.as_string())
        self.assertEqual(server.send_message.call_args[1]["to_addrs"], ["a@x.com", "c@x.com", "b@x.com"])

    def test_send_email_no_recipients(self):
        self.assertFalse(self.et.send_email({"to": []}, "S", "B"))

    def _mock_imap(self, imap_cls, raw):
        imap = imap_cls.return_value
        imap.uid.return_value = ("OK", [(b"1 (BODY[] {9}", raw), b")"])
        return imap

    @patch("src.email_tasks.imaplib.IMAP4_SSL")
    def test_fetch_and_save_attachments(self, imap_cls):
        self._mock_imap(imap_cls, _raw_email())
        info = self.et.fetch_email(b"1")
        self.assertEqual(info["sender_address"], "me@test.com")
        self.assertTrue(info["has_attachments"])
        self.assertIn("urgent", info["text_body"])
        with tempfile.TemporaryDirectory() as tmp:
            saved = self.et.save_attachments(b"1", tmp)
            self.assertEqual(saved, [os.path.join(tmp, "r.pdf")])  # path traversal stripped
            self.assertEqual(self.et.save_attachments(b"1", tmp, allowed_extensions=[".xlsx"]), [])
            again = self.et.save_attachments(b"1", tmp)
            self.assertTrue(again[0].endswith("r_1.pdf"))  # never overwrites

    @patch("src.email_tasks.imaplib.IMAP4_SSL")
    def test_search_and_mark_read(self, imap_cls):
        imap = imap_cls.return_value
        imap.uid.return_value = ("OK", [b"4 5"])
        self.assertEqual(self.et.search_emails(from_sender="a@b.com"), [b"4", b"5"])
        self.assertTrue(self.et.mark_as_read(b"4"))


class TestSMSTasks(unittest.TestCase):
    def test_send_sms(self):
        et = MagicMock(spec=EmailTasks)
        et.send_email.return_value = True
        sms = SMSTasks(et)
        self.assertTrue(sms.send_sms(["123-456-7890", "5550001111"], "hi", "att"))
        self.assertEqual(et.send_email.call_args_list[0][0][0], {"to": ["1234567890@txt.att.net"]})
        self.assertFalse(sms.send_sms(["123"], "hi", "nope"))
        self.assertFalse(sms.send_sms([], "hi"))


class TestAgent(unittest.TestCase):
    def _agent(self, config, tmp, info=None):
        et = MagicMock(spec=EmailTasks)
        et.send_email.return_value = True
        et.search_emails.return_value = [b"7"] if info else []
        et.fetch_email.return_value = info
        et.save_attachments.return_value = [os.path.join(tmp, "data/incoming_attachments/r.pdf")]
        et.mark_as_read.return_value = True
        sms = MagicMock(spec=SMSTasks)
        sms.send_sms.return_value = True
        return CommunicationAgent(config, tmp, email_tasks=et, sms_tasks=sms), et, sms

    def test_full_pipeline_and_audit(self):
        info = {"uid": "7", "sender": "Me <me@test.com>", "sender_address": "me@test.com",
                "subject": "Data Request - Urgent", "text_body": "This is urgent, new data processing",
                "html_body": "", "has_attachments": True, "attachment_names": ["r.pdf"]}
        config = {"tasks": [
            {"name": "mail", "type": "send_email", "parameters": {
                "recipients": {"to": ["a@x.com"]}, "subject_template": "Report {report_date}",
                "body_template": "Total ${sales_figure:.2f}", "attachments": ["{attachment_path_1}"]},
             "output_context_key": "sent"},
            {"name": "sms", "type": "send_sms", "parameters": {
                "phone_numbers": ["1234567890"], "message_template": "{sent[subject]}", "carrier_name": "att"}},
            {"name": "inbox", "type": "process_inbox", "parameters": {
                "search_criteria": {"from_sender": "me@test.com"},
                "rules": [
                    {"if": {"from_sender_is": "me@test.com", "subject_contains": "request"},
                     "then": {"download_attachments": True, "mark_as_read": True}},
                    {"if": {"body_contains": "URGENT"},
                     "then": {"send_sms_alert": True, "alert_phone_numbers": ["1"], "alert_carrier": "att",
                              "alert_message_template": "Saved {saved_files}"}},
                    {"if": {"body_contains": "new data processing"},
                     "then": {"reply_with_template": "Got '{subject}'", "reply_subject_template": "Re: {subject}"}},
                    {"if": {"has_attachments": False}, "then": {"mark_as_read": True}},
                ]}},
        ]}
        with tempfile.TemporaryDirectory() as tmp:
            agent, et, sms = self._agent(config, tmp, info)
            summary = agent.run()
            self.assertEqual(summary["tasks_failed"], 0)
            self.assertEqual(sms.send_sms.call_args_list[0][0][1], "Report " + agent.context["report_date"])
            et.save_attachments.assert_called_once()
            et.mark_as_read.assert_called_once()  # 4th rule must not match
            self.assertIn("r.pdf", sms.send_sms.call_args_list[1][0][1])
            reply_call = et.send_email.call_args_list[-1]
            self.assertEqual(reply_call[0][0], {"to": ["me@test.com"]})
            self.assertEqual(reply_call[0][1], "Re: Data Request - Urgent")
            with open(summary["audit_report"], encoding="utf-8") as f:
                report = json.load(f)
            self.assertEqual(report["summary"]["tasks_total"], 3)
            self.assertTrue(any(e["status"] == "SUCCESS" for e in report["entries"]))

    def test_failure_is_audited_and_alert_sent(self):
        config = {"error_alert": {"to": ["me@test.com"]}, "tasks": [
            {"name": "bad", "type": "send_email", "parameters": {
                "recipients": {"to": ["a@x.com"]}, "subject_template": "{undefined_field}", "body_template": "b"}},
            {"name": "ok", "type": "send_sms", "parameters": {
                "phone_numbers": ["1"], "message_template": "m", "carrier_name": "att"}}]}
        with tempfile.TemporaryDirectory() as tmp:
            agent, et, sms = self._agent(config, tmp)
            summary = agent.run()
            self.assertEqual(summary["failed_tasks"], ["bad"])
            self.assertEqual(summary["tasks_succeeded"], 1)  # later tasks still run
            self.assertIn("task(s) failed", et.send_email.call_args[0][1])

    def test_ignored_prefix_and_no_match(self):
        info = {"uid": "7", "sender": "m", "sender_address": "m@t.com", "subject": "Re: Data Request",
                "text_body": "", "html_body": "", "has_attachments": False, "attachment_names": []}
        config = {"tasks": [{"name": "inbox", "type": "process_inbox", "parameters": {
            "search_criteria": {"ignore_subject_prefixes": ["Re:"]},
            "rules": [{"if": {}, "then": {"mark_as_read": True}}]}}]}
        with tempfile.TemporaryDirectory() as tmp:
            agent, et, _ = self._agent(config, tmp, info)
            agent.run()
            et.mark_as_read.assert_not_called()


if __name__ == "__main__":
    unittest.main()
