"""Entry point for the Agentic Communication Automator."""
import os
import sys

from src.communication_agent import CommunicationAgent
from src.config_parser import ConfigParser
from src.template_renderer import TemplateRenderer
from src.utils import ensure_directory_exists, setup_logging

logger = setup_logging("main")


def check_required_files(config, base_dir):
    """Pre-flight: make sure every attachment referenced by send_email tasks exists."""
    renderer = TemplateRenderer()
    context = {**CommunicationAgent.default_context(), **config.get("context", {})}
    missing = []
    for task in config["tasks"]:
        if task["type"] != "send_email":
            continue
        for template in task["parameters"].get("attachments", []):
            try:
                rel_path = renderer.render(template, context)
            except ValueError:
                continue  # depends on context produced at runtime; the agent handles it
            path = rel_path if os.path.isabs(rel_path) else os.path.join(base_dir, rel_path)
            if not os.path.exists(path):
                missing.append(path)
    return missing


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "configs", "comm_pipeline_config.json")
    try:
        for sub in ("data/reports", "data/attachments", "data/incoming_attachments", "audit_reports"):
            ensure_directory_exists(os.path.join(base_dir, sub))

        logger.info(f"Loading configuration from: {config_path}")
        config = ConfigParser(config_path).load_config()

        missing = check_required_files(config, base_dir)
        if missing:
            logger.critical(f"Required attachment file(s) missing: {', '.join(missing)}")
            sys.exit(1)

        agent = CommunicationAgent(config, base_dir)
        summary = agent.run()
        logger.info(f"Done. Audit report: {summary['audit_report']}")
        if summary["tasks_failed"]:
            logger.error(f"Failed tasks: {', '.join(summary['failed_tasks'])}")
            sys.exit(2)
    except FileNotFoundError as e:
        logger.critical(f"File system error: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.critical(f"Configuration or environment variable error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected critical error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
