"""Receive and parse emails through IMAP."""
import email
import imaplib
import os
from email.header import decode_header

from .utils import ensure_directory_exists, setup_logging

logger = setup_logging(__name__)


class EmailReceiver:
    """Handles searching, reading and marking emails via IMAP."""

    def __init__(self, imap_server, email_address, password):
        self.imap_server = imap_server
        self.email_address = email_address
        self.password = password
        self.mail = None
        logger.info(f"EmailReceiver initialized for {email_address} via {imap_server}.")

    def _connect(self):
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.email_address, self.password)
            logger.info("Successfully connected and logged into IMAP server.")
            return True
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP authentication failed. Check email and app password. Error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during IMAP connect/login: {e}")
        self.mail = None
        return False

    def _disconnect(self):
        if self.mail:
            try:
                self.mail.logout()
                logger.info("Disconnected from IMAP server.")
            except Exception as e:
                logger.warning(f"Error during IMAP disconnection: {e}")
            finally:
                self.mail = None

    def search_emails(self, mailbox="INBOX", criteria="UNSEEN", from_sender=None, subject_contains=None):
        """Return a list of email UIDs (bytes) that match the criteria."""
        if not self._connect():
            return []
        try:
            self.mail.select(mailbox)
            query = [criteria]
            if from_sender:
                query += ["FROM", f'"{from_sender}"']
            if subject_contains:
                query += ["SUBJECT", f'"{subject_contains}"']
            status, data = self.mail.uid("search", None, *query)
            if status != "OK":
                logger.error(f"IMAP search failed. Status: {status}")
                return []
            uids = data[0].split()
            logger.info(f"Found {len(uids)} emails matching criteria in '{mailbox}'.")
            return uids
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []
        finally:
            self._disconnect()

    def fetch_email_content(self, uid, mailbox="INBOX", mark_as_read=True, download_attachments_dir=None):
        """Fetch one email by UID. Optionally save attachments and mark it as read."""
        if not self._connect():
            return None
        try:
            self.mail.select(mailbox)
            status, msg_data = self.mail.uid("fetch", uid, "(BODY.PEEK[])")
            if status != "OK" or not msg_data or msg_data[0] is None:
                logger.error(f"Failed to fetch email UID {uid}. Status: {status}")
                return None

            msg = email.message_from_bytes(msg_data[0][1])
            sender = self._decode_header_part(msg["From"])
            subject = self._decode_header_part(msg["Subject"])

            body = ""
            downloaded = []
            for part in msg.walk():
                if part.is_multipart():
                    continue
                disposition = str(part.get("Content-Disposition") or "")
                if "attachment" in disposition:
                    filename = self._decode_header_part(part.get_filename())
                    if filename and download_attachments_dir:
                        ensure_directory_exists(download_attachments_dir)
                        # basename prevents path traversal from malicious filenames
                        path = os.path.join(download_attachments_dir, os.path.basename(filename))
                        try:
                            with open(path, "wb") as f:
                                f.write(part.get_payload(decode=True))
                            downloaded.append(path)
                            logger.info(f"Downloaded attachment: {path}")
                        except Exception as e:
                            logger.error(f"Error downloading attachment {filename}: {e}")
                elif part.get_content_type() == "text/plain":
                    try:
                        charset = part.get_content_charset() or "utf-8"
                        body += part.get_payload(decode=True).decode(charset, errors="replace")
                    except Exception as e:
                        logger.warning(f"Could not decode text part of UID {uid}: {e}")
                        body += "[undecodable text part]"

            if mark_as_read:
                self.mail.uid("store", uid, "+FLAGS", "\\Seen")
                logger.info(f"Marked email UID {uid} as read.")

            body = body.strip()
            return {
                "uid": uid.decode("utf-8") if isinstance(uid, bytes) else str(uid),
                "sender": sender,
                "subject": subject,
                "body_snippet": body[:200] + "..." if len(body) > 200 else body,
                "attachments_downloaded": downloaded,
            }
        except Exception as e:
            logger.error(f"Error fetching/parsing email UID {uid}: {e}")
            return None
        finally:
            self._disconnect()

    @staticmethod
    def _decode_header_part(header_value):
        """Decode headers such as '=?UTF-8?B?...?=' into a normal string."""
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
