"""SMS through carrier email-to-SMS gateways (built on EmailTasks)."""
from .email_tasks import EmailTasks
from .utils import setup_logging

logger = setup_logging(__name__)


class SMSTasks:
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

    def __init__(self, email_tasks_instance):
        if not isinstance(email_tasks_instance, EmailTasks):
            raise TypeError("SMSTasks requires an instance of EmailTasks.")
        self.email_tasks = email_tasks_instance
        logger.info("SMSTasks initialized.")

    def build_gateway_address(self, phone_number, carrier_name=None):
        if carrier_name and carrier_name.lower() in self.CARRIER_GATEWAYS:
            digits = "".join(ch for ch in phone_number if ch.isdigit())
            return f"{digits}{self.CARRIER_GATEWAYS[carrier_name.lower()]}"
        if "@" in phone_number and "." in phone_number:  # already a full gateway address
            return phone_number
        return None

    def send_sms(self, phone_numbers, message, carrier_name=None):
        """Send `message` to every number. Returns True only if ALL emails were handed to SMTP."""
        if not phone_numbers:
            logger.warning("send_sms called with no phone numbers.")
            return False
        if len(message) > self.MAX_SMS_LENGTH:
            logger.warning(f"SMS is {len(message)} chars (limit ~{self.MAX_SMS_LENGTH}); it may be split/truncated.")
        ok_count = 0
        for number in phone_numbers:
            address = self.build_gateway_address(number, carrier_name)
            if address is None:
                logger.warning(f"No known carrier for {number} and it is not a gateway address. Skipping.")
                continue
            logger.info(f"Sending SMS via gateway: {address}")
            if self.email_tasks.send_email({"to": [address]}, "", message):
                ok_count += 1
        logger.info(f"SMS: {ok_count}/{len(phone_numbers)} handed to SMTP.")
        return ok_count == len(phone_numbers)
