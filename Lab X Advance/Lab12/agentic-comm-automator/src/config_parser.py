"""Load, expand and validate the agent's JSON configuration."""
import json
import os
import re

from .utils import setup_logging

logger = setup_logging(__name__)

# Matches ${ENV_NAME} (UPPER_CASE only) so that template fields such as
# "${sales_figure:.2f}" (dollar sign + format field) are NOT treated as env vars.
ENV_PATTERN = re.compile(r"\$\{([A-Z][A-Z0-9_]*)\}")

SUPPORTED_TASK_TYPES = ("send_email", "send_sms", "process_inbox")
SUPPORTED_ACTIONS = (
    "download_attachments", "allowed_extensions", "send_sms_alert", "alert_phone_numbers",
    "alert_carrier", "alert_message_template", "reply_with_template",
    "reply_subject_template", "mark_as_read",
)


def expand_env(value):
    """Recursively replace ${ENV_NAME} in strings/lists/dicts with environment values."""
    if isinstance(value, str):
        def _sub(match):
            name = match.group(1)
            env_value = os.getenv(name)
            if env_value is None or env_value.strip() == "":
                raise ValueError(f"Config references ${{{name}}} but the environment variable is not set.")
            return env_value.strip()
        return ENV_PATTERN.sub(_sub, value)
    if isinstance(value, list):
        return [expand_env(v) for v in value]
    if isinstance(value, dict):
        return {k: expand_env(v) for k, v in value.items()}
    return value


class ConfigParser:
    """Parses and validates the communication pipeline configuration."""

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}

    def load_config(self):
        if not os.path.exists(self.config_path):
            logger.critical(f"Configuration file not found: {self.config_path}")
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except json.JSONDecodeError as e:
            logger.critical(f"Invalid JSON format in config file: {e}")
            raise ValueError(f"Invalid JSON format in config file: {e}") from e

        self.config = expand_env(raw)
        self.validate(self.config)
        logger.info(f"Configuration loaded and validated from {self.config_path}")
        return self.config

    @staticmethod
    def validate(config):
        """Raise ValueError if the configuration structure is invalid."""
        if not isinstance(config, dict) or "tasks" not in config:
            raise ValueError("Missing required field in config: 'tasks'")
        if not isinstance(config["tasks"], list) or not config["tasks"]:
            raise ValueError("Config field 'tasks' must be a non-empty list.")
        if "context" in config and not isinstance(config["context"], dict):
            raise ValueError("Config field 'context' must be an object.")
        alert = config.get("error_alert")
        if alert is not None and (not isinstance(alert.get("to"), list) or not alert["to"]):
            raise ValueError("'error_alert' requires a non-empty 'to' list.")

        for i, task in enumerate(config["tasks"]):
            for field in ("type", "name"):
                if field not in task:
                    raise ValueError(f"Task {i} is missing '{field}' field.")
            ttype, label = task["type"], f"Task {i} ({task['type']}: {task['name']})"
            if ttype not in SUPPORTED_TASK_TYPES:
                raise ValueError(f"{label}: unsupported type. Use one of {SUPPORTED_TASK_TYPES}.")
            params = task.get("parameters")
            if not isinstance(params, dict):
                raise ValueError(f"{label}: 'parameters' object is required.")

            if ttype == "send_email":
                recipients = params.get("recipients")
                if not isinstance(recipients, dict) or not isinstance(recipients.get("to"), list) or not recipients["to"]:
                    raise ValueError(f"{label}: 'recipients.to' must be a non-empty list.")
                for key in ("cc", "bcc"):
                    if key in recipients and not isinstance(recipients[key], list):
                        raise ValueError(f"{label}: 'recipients.{key}' must be a list.")
                for key in ("subject_template", "body_template"):
                    if key not in params:
                        raise ValueError(f"{label}: '{key}' is required.")
                if "attachments" in params and not isinstance(params["attachments"], list):
                    raise ValueError(f"{label}: 'attachments' must be a list.")

            elif ttype == "send_sms":
                if not isinstance(params.get("phone_numbers"), list) or not params["phone_numbers"]:
                    raise ValueError(f"{label}: 'phone_numbers' must be a non-empty list.")
                if "message_template" not in params:
                    raise ValueError(f"{label}: 'message_template' is required.")

            elif ttype == "process_inbox":
                if not isinstance(params.get("search_criteria"), dict):
                    raise ValueError(f"{label}: 'search_criteria' object is required.")
                rules = params.get("rules", [])
                if not isinstance(rules, list):
                    raise ValueError(f"{label}: 'rules' must be a list.")
                for j, rule in enumerate(rules):
                    if not isinstance(rule.get("if"), dict) or not isinstance(rule.get("then"), dict):
                        raise ValueError(f"{label}: rule {j} needs 'if' and 'then' objects.")
                    unknown = set(rule["then"]) - set(SUPPORTED_ACTIONS)
                    if unknown:
                        raise ValueError(f"{label}: rule {j} has unknown actions {sorted(unknown)}.")
        logger.info("Configuration validated.")
