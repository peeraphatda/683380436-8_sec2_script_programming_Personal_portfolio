"""CommunicationAgent: runs a JSON-defined pipeline of email / SMS / inbox tasks."""
import datetime
import json
import os
import time

from .email_tasks import EmailTasks
from .sms_tasks import SMSTasks
from .template_renderer import TemplateRenderer
from .utils import ensure_directory_exists, get_env_variable, log_audit_entry, setup_logging

logger = setup_logging(__name__)

DEFAULT_ALERT_TEMPLATE = "Urgent email from {sender_address}: {subject}"


class CommunicationAgent:
    """Orchestrates tasks, keeps a shared context for templating, writes an audit report."""

    def __init__(self, config, base_dir, email_tasks=None, sms_tasks=None):
        self.config = config
        self.base_dir = base_dir
        self.audit_log = []
        self.context = {}
        self.start_time = datetime.datetime.now()
        self.template_renderer = TemplateRenderer()

        if email_tasks is None:  # build real handlers from environment variables
            try:
                email_tasks = EmailTasks(
                    get_env_variable("SMTP_SERVER"),
                    int(get_env_variable("SMTP_PORT")),
                    get_env_variable("IMAP_SERVER"),
                    get_env_variable("SENDER_EMAIL"),
                    get_env_variable("SENDER_APP_PASSWORD"),
                )
            except ValueError as e:
                logger.critical(f"Agent initialization failed: {e}")
                raise
        self.email_tasks = email_tasks
        self.sms_tasks = sms_tasks or SMSTasks(email_tasks)

        # Task dispatcher: config 'type' -> handler
        self._handlers = {
            "send_email": self._handle_send_email,
            "send_sms": self._handle_send_sms,
            "process_inbox": self._handle_process_inbox,
        }
        logger.info("CommunicationAgent initialized.")

    # ------------------------------------------------------------ context
    @staticmethod
    def default_context():
        """Simulated data (e.g. produced by an earlier data agent)."""
        return {
            "report_name": "DailySalesSummary",
            "report_date": datetime.date.today().strftime("%Y-%m-%d"),
            "sales_figure": 12345.67,
            "total_customers": 500,
            "attachment_path_1": "data/reports/sales_report.pdf",
            "attachment_path_2": "data/reports/summary_data.xlsx",
        }

    def _update_context(self, key, value):
        self.context[key] = value

    def _render(self, template, extra=None):
        return self.template_renderer.render(template, {**self.context, **(extra or {})})

    def _resolve_path(self, path):
        return path if os.path.isabs(path) else os.path.join(self.base_dir, path)

    def _audit(self, status, message, task_type="N/A", details=None):
        return log_audit_entry(self.audit_log, status, message, task_type, details)

    # ------------------------------------------------------------ handlers
    def _handle_send_email(self, params):
        recipients = {k: [self._render(a) for a in v] for k, v in params["recipients"].items()}
        subject = self._render(params["subject_template"])
        body = self._render(params["body_template"])
        attachments = [self._resolve_path(self._render(p)) for p in params.get("attachments", [])]
        ok = self.email_tasks.send_email(recipients, subject, body, attachments, params.get("is_html", False))
        return ok, {"recipients": recipients, "subject": subject,
                    "attachments": [os.path.basename(a) for a in attachments]}

    def _handle_send_sms(self, params):
        numbers = [self._render(p) for p in params["phone_numbers"]]
        message = self._render(params["message_template"])
        ok = self.sms_tasks.send_sms(numbers, message, params.get("carrier_name"))
        return ok, {"phone_numbers": numbers, "message": message}

    def _handle_process_inbox(self, params):
        mailbox = params.get("mailbox", "INBOX")
        criteria = params["search_criteria"]
        dest_dir = self._resolve_path(params.get("download_attachments_base_dir", "data/incoming_attachments"))
        rules = params.get("rules", [])
        ignore_prefixes = [p.lower() for p in criteria.get("ignore_subject_prefixes", [])]

        if params.get("wait_before_seconds"):  # give the mail server time to deliver the demo email
            logger.info(f"Waiting {params['wait_before_seconds']}s for email delivery...")
            time.sleep(params["wait_before_seconds"])

        def _search():
            return self.email_tasks.search_emails(
                mailbox=mailbox,
                criteria=criteria.get("status", "UNSEEN"),
                from_sender=self._render(criteria["from_sender"]) if criteria.get("from_sender") else None,
                subject_contains=self._render(criteria["subject_contains"]) if criteria.get("subject_contains") else None,
            )

        uids = _search()
        for _ in range(int(params.get("retries", 0))):
            if uids:
                break
            time.sleep(params.get("retry_delay_seconds", 5))
            uids = _search()

        summaries, all_ok = [], True
        for uid in uids:
            info = self.email_tasks.fetch_email(uid, mailbox)
            if not info:
                self._audit("ERROR", "Could not fetch email", "process_inbox", {"uid": str(uid)})
                all_ok = False
                continue
            if any(info["subject"].lower().startswith(p) for p in ignore_prefixes):
                logger.info(f"Skipping email UID {info['uid']} (ignored subject prefix).")
                continue
            summary, ok = self._apply_rules(info, uid, rules, dest_dir, mailbox)
            summaries.append(summary)
            all_ok = all_ok and ok
        if not uids:
            logger.info("No emails found matching search criteria.")
        return all_ok, {"processed_emails": summaries}

    # ------------------------------------------------------------ rules
    def _rule_matches(self, cond, info):
        """All conditions must hold (AND). String comparisons are case-insensitive."""
        subject, body = info.get("subject", "").lower(), info.get("text_body", "").lower()
        if "from_sender_is" in cond and \
                self._render(cond["from_sender_is"], info).strip().lower() != info.get("sender_address", ""):
            return False
        if "subject_contains" in cond and self._render(cond["subject_contains"], info).lower() not in subject:
            return False
        if "body_contains" in cond and self._render(cond["body_contains"], info).lower() not in body:
            return False
        if "has_attachments" in cond and bool(cond["has_attachments"]) != bool(info.get("has_attachments")):
            return False
        return True

    def _template_vars(self, info, saved_files, dest_dir):
        rel = lambda p: os.path.relpath(p, self.base_dir)
        return {
            **info,
            "attachment_names": ", ".join(info.get("attachment_names", [])),
            "saved_files": ", ".join(rel(p) for p in saved_files),
            "saved_to": rel(dest_dir),
        }

    def _apply_rules(self, info, uid, rules, dest_dir, mailbox):
        summary = {"uid": info["uid"], "sender": info["sender"], "subject": info["subject"],
                   "rules_matched": [], "attachments_saved": [], "sms_alerts_sent": 0,
                   "replies_sent": 0, "marked_as_read": False}
        ok = True
        saved_files = []
        for idx, rule in enumerate(rules):
            name = rule.get("name", f"rule_{idx + 1}")
            if not self._rule_matches(rule.get("if", {}), info):
                continue
            summary["rules_matched"].append(name)
            self._audit("INFO", f"Rule '{name}' matched email UID {info['uid']}", "process_inbox")
            then = rule["then"]
            try:
                if then.get("download_attachments"):
                    saved = self.email_tasks.save_attachments(uid, dest_dir, mailbox, then.get("allowed_extensions"))
                    saved_files += saved
                    summary["attachments_saved"] = [os.path.relpath(p, self.base_dir) for p in saved_files]
                    self._audit("SUCCESS", f"Downloaded {len(saved)} attachment(s)", "process_inbox",
                                {"files": summary["attachments_saved"]})
                tvars = self._template_vars(info, saved_files, dest_dir)

                if then.get("send_sms_alert"):
                    numbers = [self._render(p) for p in then.get("alert_phone_numbers", [])]
                    message = self._render(then.get("alert_message_template", DEFAULT_ALERT_TEMPLATE), tvars)
                    if self.sms_tasks.send_sms(numbers, message, then.get("alert_carrier")):
                        summary["sms_alerts_sent"] += 1
                        self._audit("SUCCESS", "SMS alert sent", "process_inbox", {"message": message})
                    else:
                        ok = False
                        self._audit("ERROR", "SMS alert failed", "process_inbox", {"message": message})

                if then.get("reply_with_template"):
                    subject = self._render(then.get("reply_subject_template", "Re: {subject}"), tvars)
                    body = self._render(then["reply_with_template"], tvars)
                    if self.email_tasks.send_email({"to": [info["sender_address"]]}, subject, body):
                        summary["replies_sent"] += 1
                        self._audit("SUCCESS", "Auto-reply sent", "process_inbox", {"subject": subject})
                    else:
                        ok = False
                        self._audit("ERROR", "Auto-reply failed", "process_inbox", {"subject": subject})

                if then.get("mark_as_read"):  # last, so a failed action leaves the email unread
                    summary["marked_as_read"] = bool(self.email_tasks.mark_as_read(uid, mailbox))
                    self._audit("SUCCESS" if summary["marked_as_read"] else "ERROR",
                                "Mark as read", "process_inbox", {"uid": info["uid"]})
                    ok = ok and summary["marked_as_read"]
            except Exception as e:
                ok = False
                self._audit("ERROR", f"Rule '{name}' failed: {e}", "process_inbox", {"error": str(e)})
        if not summary["rules_matched"]:
            logger.info(f"No rule matched for email UID {info['uid']}.")
        return summary, ok

    # ------------------------------------------------------------ run
    def _process_task(self, task):
        name, ttype = task["name"], task["type"]
        logger.info(f"Executing task: '{name}' (type: {ttype})")
        self._audit("INFO", f"Starting task '{name}'", ttype)
        handler = self._handlers.get(ttype)
        if handler is None:
            self._audit("ERROR", f"Unsupported task type: {ttype}", ttype)
            return False
        try:
            ok, output = handler(task.get("parameters", {}))
        except Exception as e:
            logger.error(f"Error during task '{name}': {e}", exc_info=True)
            self._audit("ERROR", f"Task '{name}' raised an error: {e}", ttype, {"error": str(e)})
            return False
        key = task.get("output_context_key")
        if key and output is not None:
            self._update_context(key, output)
        self._audit("SUCCESS" if ok else "ERROR",
                    f"Task '{name}' {'completed successfully' if ok else 'failed'}.", ttype, output)
        return ok

    def _send_error_alert(self, failed_names):
        alert = self.config.get("error_alert")
        if not alert or not failed_names:
            return
        errors = [f"- {e['message']}" for e in self.audit_log if e["status"] in ("ERROR", "CRITICAL")]
        body = (f"{len(failed_names)} task(s) failed: {', '.join(failed_names)}\n\n"
                "Errors:\n" + "\n".join(errors))
        ok = self.email_tasks.send_email({"to": alert["to"]},
                                         f"[CommunicationAgent] {len(failed_names)} task(s) failed", body)
        self._audit("INFO" if ok else "CRITICAL", "Error alert email " + ("sent" if ok else "FAILED"), "error_alert")

    def _generate_audit_report(self, summary):
        out_dir = os.path.join(self.base_dir, "audit_reports")
        ensure_directory_exists(out_dir)
        path = os.path.join(out_dir, f"audit_report_comm_{datetime.datetime.now():%Y%m%d_%H%M%S}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"summary": summary, "entries": self.audit_log}, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Audit report saved to: {path}")
        return path

    def run(self):
        """Execute every task in order. Returns a summary dict (incl. audit report path)."""
        logger.info("Starting Communication Agent run...")
        self._audit("INFO", "Communication Agent started.", "agent_run")
        self.context.update(self.default_context())
        self.context.update(self.config.get("context", {}))

        failed = []
        for task in self.config["tasks"]:
            if not self._process_task(task):
                failed.append(task["name"])
        self._send_error_alert(failed)

        duration = (datetime.datetime.now() - self.start_time).total_seconds()
        total = len(self.config["tasks"])
        summary = {"tasks_total": total, "tasks_succeeded": total - len(failed),
                   "tasks_failed": len(failed), "failed_tasks": failed,
                   "duration_seconds": round(duration, 2)}
        self._audit("INFO", f"Agent finished in {duration:.2f}s", "agent_run_summary", summary)
        summary["audit_report"] = self._generate_audit_report(summary)
        logger.info(f"Agent finished: {summary['tasks_succeeded']}/{total} tasks succeeded.")
        return summary
