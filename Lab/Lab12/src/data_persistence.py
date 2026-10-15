"""Handles all JSON file I/O and (de)serialization of Task objects."""
import json
import logging
import os

from .task import Task, DueDateTask, PriorityTask

logger = logging.getLogger(__name__)

TASK_TYPES = {
    "Task": Task,
    "DueDateTask": DueDateTask,
    "PriorityTask": PriorityTask,
}


class DataPersistence:
    """Loads and saves tasks to/from a JSON file."""

    def __init__(self, data_file="data/tasks.json"):
        # Relative paths are resolved against the project root;
        # absolute paths (e.g. in tests) are used as-is.
        project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        self._data_file_path = os.path.abspath(os.path.join(project_root, data_file))

    def load_tasks(self):
        """Loads tasks and rebuilds the right Task subclass from '_type'."""
        if not os.path.exists(self._data_file_path):
            os.makedirs(os.path.dirname(self._data_file_path), exist_ok=True)
            return []
        try:
            with open(self._data_file_path, "r", encoding="utf-8") as f:
                raw_tasks = json.load(f)
        except json.JSONDecodeError:
            print("Warning: tasks.json is empty or corrupted. Starting with an empty task list.")
            return []
        except OSError as e:
            print(f"Could not read tasks file: {e}. Starting with an empty list.")
            return []

        loaded = []
        for t_dict in raw_tasks:
            t_dict = dict(t_dict)
            task_type = t_dict.pop("_type", "Task")
            t_dict.setdefault("tags", [])  # old data without tags
            cls = TASK_TYPES.get(task_type)
            if cls is None:
                print(f"Warning: Unknown task type '{task_type}'. "
                      f"Skipping task ID {t_dict.get('id', 'N/A')}.")
                continue
            try:
                loaded.append(cls(**t_dict))
            except (TypeError, ValueError) as e:
                print(f"Warning: Skipping invalid task ID {t_dict.get('id', 'N/A')}: {e}")
        logger.info("Loaded %d tasks.", len(loaded))
        return loaded

    def save_tasks(self, tasks):
        """Saves tasks using each task's polymorphic to_dict()."""
        os.makedirs(os.path.dirname(self._data_file_path), exist_ok=True)
        with open(self._data_file_path, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in tasks], f, indent=4, ensure_ascii=False)
        logger.info("Saved %d tasks.", len(tasks))
