"""Orchestrates the email / SMS automation tasks."""
import os
import sys
import time

from src.email_receiver import EmailReceiver
from src.email_sender import EmailSender
from src.sms_gateway import SMSGateway
from src.utils import ensure_directory_exists, get_env_variable, setup_logging

logger = setup_logging("main")

DEMO_SUBJECT = "Python Test: Email for Receiving Demo"


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    attachments_dir = os.path.join(data_dir, "attachments")
    ensure_directory_exists(attachments_dir)

    # --- Load credentials from environment variables ---
    try:
        sender_email = get_env_variable("SENDER_EMAIL")
        sender_app_password = get_env_variable("SENDER_APP_PASSWORD")
        smtp_server = get_env_variable("SMTP_SERVER")
        smtp_port = int(get_env_variable("SMTP_PORT"))
        imap_server = get_env_variable("IMAP_SERVER")
        test_recipient_email = get_env_variable("TEST_RECIPIENT_EMAIL")
        test_sms_phone_number = get_env_variable("TEST_SMS_PHONE_NUMBER")
        test_sms_carrier = get_env_variable("TEST_SMS_CARRIER")
    except ValueError as e:
        logger.critical(f"Configuration error: {e}")
        sys.exit(1)

    email_sender = EmailSender(smtp_server, smtp_port, sender_email, sender_app_password)
    email_receiver = EmailReceiver(imap_server, sender_email, sender_app_password)
    sms_gateway = SMSGateway(email_sender)

    # --- Task 1: plain-text email ---
    logger.info("--- Task 1: Sending a simple plaintext email ---")
    email_sender.send_email(
        recipient_email=test_recipient_email,
        subject="Automated Python Test Email",
        body="Hello from your Python automation script! This is a plain text email.",
    )
    time.sleep(2)

    # --- Task 2: email with attachment ---
    logger.info("--- Task 2: Sending an email with an attachment ---")
    attachment_file_path = os.path.join(data_dir, "dummy_report.pdf")
    if os.path.exists(attachment_file_path):
        email_sender.send_email(
            recipient_email=test_recipient_email,
            subject="Python Test Email with Attachment - Daily Report",
            body="Please find the daily report attached.",
            attachment_path=attachment_file_path,
        )
    else:
        logger.warning(f"Attachment not found at '{attachment_file_path}'. Skipping.")
        attachment_file_path = None
    time.sleep(2)

    # --- Task 3: SMS via email gateway ---
    logger.info("--- Task 3: Sending an SMS via email gateway ---")
    sms_gateway.send_sms(
        phone_number=test_sms_phone_number,
        message="Hello from Python! This is an automated SMS via email gateway.",
        carrier_name=test_sms_carrier,
    )
    time.sleep(5)

    # --- Task 4: receive and process emails ---
    logger.info("--- Task 4: Receiving and processing emails ---")
    email_sender.send_email(
        recipient_email=sender_email,  # send to self so there is something to find
        subject=DEMO_SUBJECT,
        body="This email is specifically for the receiving demo. It has an attachment!",
        attachment_path=attachment_file_path,
    )
    logger.info("Sent a demo email to self. Waiting for delivery...")
    time.sleep(10)

    uids = email_receiver.search_emails(
        criteria="UNSEEN", from_sender=sender_email, subject_contains=DEMO_SUBJECT
    )
    if not uids:
        logger.info("No matching unread emails found for receiving demo.")
    for uid in uids:
        logger.info(f"Processing email UID: {uid.decode('utf-8')}")
        details = email_receiver.fetch_email_content(
            uid, mark_as_read=True, download_attachments_dir=attachments_dir
        )
        if not details:
            logger.error(f"Could not retrieve details for UID: {uid.decode('utf-8')}")
            continue
        logger.info(f"  Sender: {details['sender']}")
        logger.info(f"  Subject: {details['subject']}")
        logger.info(f"  Body Snippet: {details['body_snippet']}")
        if details["attachments_downloaded"]:
            logger.info(f"  Attachments downloaded: {', '.join(details['attachments_downloaded'])}")
        else:
            logger.info("  No attachments downloaded for this email.")

    logger.info("--- All communication automation tasks completed ---")


if __name__ == "__main__":
    main()
