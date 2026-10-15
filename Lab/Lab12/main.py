"""Entry point for the Enhanced Task Manager application."""
import logging

from src.task_manager import TaskManager
from src.cli_interface import CLIInterface


def main():
    # Change to logging.INFO / DEBUG to see debug output
    logging.basicConfig(level=logging.WARNING,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    manager = TaskManager()
    cli = CLIInterface(manager)
    cli.run()


if __name__ == "__main__":
    main()
