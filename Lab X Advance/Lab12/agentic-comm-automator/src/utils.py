"""Logging, environment-variable loading, directory helpers and audit logging."""
import datetime
import logging
import os

from dotenv import load_dotenv

# Load variables from .env (if present) into the process environment
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def setup_logging(name, level=logging.INFO):
    """Return a logger configured for the given module name."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        logger.propagate = False  # avoid duplicate lines from the root logger
    return logger


def get_env_variable(var_name):
    """Return an environment variable or raise ValueError if it is missing/empty."""
    value = os.getenv(var_name)
    if value is None or value.strip() == "":
        raise ValueError(
            f"Environment variable '{var_name}' not set. "
            "Please check your .env file or environment settings."
        )
    return value.strip()


def ensure_directory_exists(path):
    """Create the directory (and parents) if it does not exist."""
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        logging.error(f"Error creating directory {path}: {e}")
        raise


def log_audit_entry(audit_log_list, status, message, task_type="N/A", details=None):
    """Append an entry to the audit log list and echo it to the console."""
    entry = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "task_type": task_type,
        "message": message,
        "details": details if details else {},
    }
    audit_log_list.append(entry)
    if status in ("ERROR", "CRITICAL"):
        logging.error(f"AUDIT {status}: {message} | Task: {task_type} | Details: {entry['details']}")
    else:
        logging.info(f"AUDIT {status}: {message} | Task: {task_type}")
    return entry
