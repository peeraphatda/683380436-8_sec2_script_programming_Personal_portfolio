# LabADV-week-11/main.py
import argparse
import os

from src.config_parser import ConfigParser
from src.document_agent import DocumentAgent
from src.utils import setup_logging

logger = setup_logging(__name__)


def main():
    """Main entry point for the document automation agent."""
    arg_parser = argparse.ArgumentParser(description="Document Automation Agent")
    arg_parser.add_argument("-c", "--config",
                            default=os.path.join('configs', 'document_automation_config.json'),
                            help="Path to the JSON config file")
    arg_parser.add_argument("-t", "--task", action="append",
                            help="Run only this task id (can be repeated)")
    arg_parser.add_argument("--list", action="store_true", help="List tasks and exit")
    args = arg_parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = args.config if os.path.isabs(args.config) else os.path.join(base_dir, args.config)

    try:
        config = ConfigParser(config_path).load_config()

        if args.list:
            for t in config["tasks"]:
                flag = "" if t.get("enabled", True) else " [disabled: use -t]"
                print(f"{t['id']:<24} {t['type']}.{t['action']:<16} {t.get('description', '')}{flag}")
            return 0

        logger.info("--- Starting Document Automation Workflow ---")
        agent = DocumentAgent(config, base_dir=base_dir)
        agent.run(only=args.task)
        logger.info("--- Document Automation Workflow Completed ---")
        return 1 if any(r["status"] == "failed" for r in agent.results) else 0
    except Exception as e:
        logger.critical(f"Execution failed: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
