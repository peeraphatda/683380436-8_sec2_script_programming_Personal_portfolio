# main.py - Orchestrator
import sys

# แก้ปัญหาภาษาไทยเพี้ยนใน Terminal (Windows / PowerShell)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
except AttributeError:
    pass

from src.task_manager import TaskManager
from src.cli_interface import CLIInterface


def main():
    manager = TaskManager()
    cli = CLIInterface(manager)
    cli.run()


if __name__ == "__main__":
    main()
