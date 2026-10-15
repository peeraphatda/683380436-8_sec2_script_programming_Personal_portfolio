"""Send SMS through carrier email-to-SMS gateways."""
from .email_sender import EmailSender
from .utils import setup_logging

logger = setup_logging(__name__)


class SMSGateway:
    """Simplified SMS interface built on top of EmailSender."""

    CARRIER_GATEWAYS = {
        "att": "@txt.att.net",
        "verizon": "@vtext.com",
        "tmobile": "@tmomail.net",
        "sprint": "@messaging.sprintpcs.com",
        "boost": "@sms.boostmobile.com",
        "cricket": "@mms.cricketwireless.net",
        "us_cellular": "@email.uscc.net",
    }
    MAX_SMS_LENGTH = 160

    def __init__(self, email_sender_instance):
        if not isinstance(email_sender_instance, EmailSender):
            raise TypeError("SMSGateway requires an instance of EmailSender.")
        self.email_sender = email_sender_instance
        logger.info("SMSGateway initialized.")

    def build_gateway_address(self, phone_number, carrier_name=None):
        """Return the gateway email address, or None if it cannot be determined."""
        if carrier_name and carrier_name.lower() in self.CARRIER_GATEWAYS:
            digits = "".join(ch for ch in phone_number if ch.isdigit())
            return f"{digits}{self.CARRIER_GATEWAYS[carrier_name.lower()]}"
        if "@" in phone_number and "." in phone_number:  # already a full gateway address
            return phone_number
        return None

    def send_sms(self, phone_number, message, carrier_name=None):
        """Send an SMS. Returns True if the email was handed to the SMTP server."""
        address = self.build_gateway_address(phone_number, carrier_name)
        if address is None:
            logger.warning("Unknown carrier and phone_number is not a gateway address. Cannot send SMS.")
            return False
        if len(message) > self.MAX_SMS_LENGTH:
            logger.warning(f"Message is {len(message)} chars; it may be truncated or split (limit ~160).")
        logger.info(f"Sending SMS via gateway: {address}")
        return self.email_sender.send_email(address, "", message)
