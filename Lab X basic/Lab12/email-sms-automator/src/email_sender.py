"""Send emails (plain text / HTML / attachments) through SMTP."""
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .utils import setup_logging

logger = setup_logging(__name__)


class EmailSender:
    """Handles sending emails via SMTP with STARTTLS."""

    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.server = None
        logger.info(f"EmailSender initialized for {sender_email} via {smtp_server}:{smtp_port}.")

    def _connect(self):
        """Connect, secure the connection with TLS and log in."""
        try:
            self.server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            self.server.starttls()
            self.server.login(self.sender_email, self.sender_password)
            logger.info("Successfully connected and logged into SMTP server.")
            return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed. Check email and app password. Error: {e}")
        except (smtplib.SMTPConnectError, OSError) as e:
            logger.error(f"SMTP connection failed. Check server address and port. Error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during SMTP connect/login: {e}")
        self.server = None
        return False

    def _disconnect(self):
        if self.server:
            try:
                self.server.quit()
                logger.info("Disconnected from SMTP server.")
            except Exception as e:
                logger.warning(f"Error during SMTP disconnection: {e}")
            finally:
                self.server = None

    def build_message(self, recipient_email, subject, body, attachment_path=None, is_html=False):
        """Build a MIME message (separate from sending so it can be tested)."""
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html" if is_html else "plain", "utf-8"))

        if attachment_path:
            try:
                with open(attachment_path, "rb") as f:
                    filename = os.path.basename(attachment_path)
                    part = MIMEApplication(f.read(), Name=filename)
                part["Content-Disposition"] = f'attachment; filename="{filename}"'
                msg.attach(part)
                logger.info(f"Attached file: {attachment_path}")
            except FileNotFoundError:
                logger.error(f"Attachment not found: {attachment_path}. Sending without it.")
            except Exception as e:
                logger.error(f"Error attaching {attachment_path}: {e}. Sending without it.")
        return msg

    def send_email(self, recipient_email, subject, body, attachment_path=None, is_html=False):
        """Send an email. Returns True on success, False otherwise."""
        msg = self.build_message(recipient_email, subject, body, attachment_path, is_html)
        if not self._connect():
            return False
        try:
            self.server.send_message(msg)
            logger.info(f"Email sent successfully to {recipient_email} with subject: '{subject}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}. Error: {e}")
            return False
        finally:
            self._disconnect()
