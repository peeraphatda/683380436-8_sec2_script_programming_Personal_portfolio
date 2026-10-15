# main.py
import argparse
import os
import sys

from src.config_parser import ConfigParser
from src.spreadsheet_agent import SpreadsheetAgent
from src.utils import setup_logging

logger = setup_logging("main")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join("configs", "example_spreadsheet_config.json")


def main():
    parser = argparse.ArgumentParser(description="Agentic Spreadsheet Processor")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="path to JSON config file")
    args = parser.parse_args()

    # ทำให้ path แบบ relative ใน config (เช่น data/input_data.xlsx) ใช้ได้ไม่ว่ารันจากโฟลเดอร์ไหน
    os.chdir(PROJECT_ROOT)

    try:
        os.makedirs("data", exist_ok=True)
        logger.info(f"Loading configuration from: {args.config}")
        config = ConfigParser(args.config).load_config()

        if not os.path.exists(config["input_file"]):
            logger.critical(f"Input file not found: '{config['input_file']}'. Run `python create_dummy_data.py` first.")
            return 1

        agent = SpreadsheetAgent(config)
        ok = agent.run()
        if not ok or agent.has_errors():
            logger.warning("Finished with errors. See the 'Audit Log' sheet for details.")
            return 1
        logger.info(f"Done. Report: {config['output_file']}")
        return 0
    except FileNotFoundError as e:
        logger.critical(f"File system error: {e}")
    except ValueError as e:
        logger.critical(f"Configuration error: {e}")
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
