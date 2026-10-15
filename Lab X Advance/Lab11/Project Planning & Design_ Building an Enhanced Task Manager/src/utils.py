# LabADV-week-11/src/utils.py
import json
import logging
import os
from datetime import datetime

# Configure basic logging for the utility module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_logging(name, level=logging.INFO):
    """Sets up a logger for specific modules."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger


def ensure_directory_exists(path):
    """Ensures that a directory exists, creating it if necessary."""
    try:
        os.makedirs(path, exist_ok=True)
        logging.info(f"Directory ensured: {path}")
    except OSError as e:
        logging.error(f"Error creating directory {path}: {e}")
        raise


def timestamp(fmt="%Y%m%d_%H%M%S"):
    return datetime.now().strftime(fmt)


def today():
    return datetime.now().strftime("%Y-%m-%d")


def write_audit_report(reports_dir, results, project):
    """Writes a human-readable audit report of every executed task."""
    ensure_directory_exists(reports_dir)
    path = os.path.join(reports_dir, f"audit_report_{timestamp()}.txt")
    ok = sum(1 for r in results if r["status"] == "success")
    lines = [
        "=" * 60,
        f"AUDIT REPORT - {project.get('name', 'Document Automation Agent')}",
        "=" * 60,
        f"Generated : {datetime.now().isoformat(timespec='seconds')}",
        f"Author    : {project.get('author', '-')}",
        f"Version   : {project.get('version', '-')}",
        f"Tasks     : {len(results)} total, {ok} success, {len(results) - ok} failed",
        "-" * 60,
    ]
    for i, r in enumerate(results, 1):
        lines += [
            f"{i}. [{r['status'].upper()}] {r['id']} ({r['type']}.{r['action']})",
            f"   Description : {r.get('description', '')}",
            f"   Duration    : {r['duration']:.3f}s",
            f"   Detail      : {r['detail']}",
        ]
    lines += ["=" * 60, "RAW JSON:", json.dumps(results, indent=2, ensure_ascii=False)]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path
