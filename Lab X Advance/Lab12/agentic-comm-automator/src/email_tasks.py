"""Sending (SMTP) and receiving (IMAP) emails for the agent."""
import email
import imaplib
import os
import re
import smtplib
from contextlib import contextmanager
from email.header import Header, decode_header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr

from .utils import ensure_directory_exists, setup_logging

logger = setup_logging(__name__)


def _uid_str(uid):
    return uid.decode("utf-8") if isinstance(uid, bytes) else str(uid)


def _unique_path(directory, filename):
    """Return a path inside `directory` that does not overwrite an existing file."""
    base, ext = os.path.splitext(filename)
    path, n = os.path.join(directory, filename), 1
    while os.path.exists(path):
        path = os.path.join(directory, f"{base}_{n}{ext}")
        n += 1
    return path


class EmailTasks:
    """SMTP sending with CC/BCC/attachments and IMAP search/fetch/download/mark-as-read."""

    def __init__(self, smtp_server, smtp_port, imap_server, sender_email, sender_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.imap_server = imap_server
        self.sender_email = sender_email
        self.sender_password = sender_password
        logger.info(f"EmailTasks initialized for {sender_email}.")

    # ------------------------------------------------------------------ SMTP
    def build_message(self, recipients, subject, body, attachments=None, is_html=False):
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = ", ".join(recipients.get("to", []))
        if recipients.get("cc"):
            msg["Cc"] = ", ".join(recipients["cc"])  # BCC is deliberately NOT put in headers
        msg["Subject"] = Header(subject, "utf-8")
        msg.attach(MIMEText(body, "html" if is_html else "plain", "utf-8"))

        for path in attachments or []:
            if not os.path.exists(path):
                logger.warning(f"Attachment file not found: {path}. Skipping.")
                continue
            try:
                name = os.path.basename(path)
                with open(path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=name)
                part["Content-Disposition"] = f'attachment; filename="{name}"'
                msg.attach(part)
                logger.info(f"Attached file: {path}")
            except Exception as e:
                logger.error(f"Error attaching file {path}: {e}")
        return msg

    def send_email(self, recipients, subject, body, attachments=None, is_html=False):
        """Send an email. `recipients` = {'to': [...], 'cc': [...], 'bcc': [...]}. Returns bool."""
        all_recipients = [r for key in ("to", "cc", "bcc") for r in recipients.get(key, [])]
        if not all_recipients:
            logger.error("No recipients specified for email.")
            return False
        msg = self.build_message(recipients, subject, body, attachments, is_html)
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg, from_addr=self.sender_email, to_addrs=all_recipients)
            logger.info(f"Email sent to {', '.join(recipients.get('to', []))} | Subject: '{subject}'")
            return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed. Check email and app password. Error: {e}")
        except (smtplib.SMTPException, OSError) as e:
            logger.error(f"Failed to send email: {e}")
        return False

    # ------------------------------------------------------------------ IMAP
    @contextmanager
    def _imap_session(self, mailbox="INBOX"):
        mail = imaplib.IMAP4_SSL(self.imap_server)
        try:
            mail.login(self.sender_email, self.sender_password)
            mail.select(mailbox)
            yield mail
        finally:
            try:
                mail.logout()
            except Exception:
                pass

    @staticmethod
    def _decode_header_part(header_value):
        if header_value is None:
            return ""
        result = ""
        for part, charset in decode_header(header_value):
            if isinstance(part, bytes):
                try:
                    result += part.decode(charset or "utf-8")
                except (LookupError, UnicodeDecodeError):
                    result += part.decode("latin-1", errors="replace")
            else:
                result += part
        return result.strip()

    def search_emails(self, mailbox="INBOX", criteria="UNSEEN", from_sender=None, subject_contains=None):
        """Return matching email UIDs (list of bytes)."""
        try:
            with self._imap_session(mailbox) as mail:
                query = [criteria]
                if from_sender:
                    query += ["FROM", f'"{from_sender}"']
                if subject_contains:
                    query += ["SUBJECT", f'"{subject_contains}"']
                status, data = mail.uid("search", None, *query)
                if status != "OK":
                    logger.error(f"IMAP search failed. Status: {status}")
                    return []
                uids = data[0].split()
                logger.info(f"Found {len(uids)} email(s) matching criteria in '{mailbox}'.")
                return uids
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP error while searching (check app password / IMAP enabled): {e}")
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
        return []

    def _get_message(self, mail, uid):
        status, data = mail.uid("fetch", uid, "(BODY.PEEK[])")  # PEEK: does not mark as read
        if status != "OK" or not data or data[0] is None:
            raise RuntimeError(f"Failed to fetch email UID {_uid_str(uid)} (status {status}).")
        return email.message_from_bytes(data[0][1])

    @staticmethod
    def _attachment_parts(msg):
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get_filename():
                yield part

    def fetch_email(self, uid, mailbox="INBOX"):
        """Parse one email (no side effects). Returns a dict or None."""
        try:
            with self._imap_session(mailbox) as mail:
                msg = self._get_message(mail, uid)
        except Exception as e:
            logger.error(f"Error fetching/parsing email UID {_uid_str(uid)}: {e}")
            return None

        text_body, html_body = "", ""
        for part in msg.walk():
            if part.get_content_maintype() == "multipart" or part.get_filename():
                continue
            ctype = part.get_content_type()
            if ctype not in ("text/plain", "text/html"):
                continue
            try:
                payload = part.get_payload(decode=True) or b""
                text = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
            except Exception as e:
                logger.warning(f"Could not decode a text part of UID {_uid_str(uid)}: {e}")
                continue
            if ctype == "text/plain":
                text_body += text
            else:
                html_body += text
        if not text_body and html_body:  # fall back to crude HTML->text so rules still work
            text_body = re.sub(r"<[^>]+>", " ", html_body)

        sender = self._decode_header_part(msg["From"])
        names = [self._decode_header_part(p.get_filename()) for p in self._attachment_parts(msg)]
        return {
            "uid": _uid_str(uid),
            "sender": sender,
            "sender_address": parseaddr(sender)[1].lower(),
            "subject": self._decode_header_part(msg["Subject"]),
            "text_body": text_body.strip(),
            "html_body": html_body,
            "has_attachments": bool(names),
            "attachment_names": names,
        }

    def save_attachments(self, uid, dest_dir, mailbox="INBOX", allowed_extensions=None):
        """Download attachments (optionally only certain extensions). Returns saved file paths."""
        allowed = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in (allowed_extensions or [])}
        saved = []
        try:
            with self._imap_session(mailbox) as mail:
                msg = self._get_message(mail, uid)
            ensure_directory_exists(dest_dir)
            for part in self._attachment_parts(msg):
                filename = os.path.basename(self._decode_header_part(part.get_filename()).replace("\\", "/"))
                if not filename:
                    continue
                if allowed and os.path.splitext(filename)[1].lower() not in allowed:
                    logger.info(f"Skipping attachment '{filename}' (extension not allowed).")
                    continue
                path = _unique_path(dest_dir, filename)
                with open(path, "wb") as f:
                    f.write(part.get_payload(decode=True) or b"")
                saved.append(path)
                logger.info(f"Downloaded attachment: {path}")
        except Exception as e:
            logger.error(f"Error downloading attachments for UID {_uid_str(uid)}: {e}")
        return saved

    def mark_as_read(self, uid, mailbox="INBOX"):
        try:
            with self._imap_session(mailbox) as mail:
                status, _ = mail.uid("store", uid, "+FLAGS", "\\Seen")
            logger.info(f"Marked email UID {_uid_str(uid)} as read.")
            return status == "OK"
        except Exception as e:
            logger.error(f"Error marking UID {_uid_str(uid)} as read: {e}")
            return False
