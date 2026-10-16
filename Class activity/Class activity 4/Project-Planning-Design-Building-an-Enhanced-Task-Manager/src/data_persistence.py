# src/data_persistence.py  (Data Layer)
import json
import os

from .task import Task, DueDateTask, PriorityTask


class DataPersistence:
    """Handles loading/saving tasks to/from a JSON file (all file I/O lives here)."""

    TYPE_MAP = {"Task": Task, "DueDateTask": DueDateTask, "PriorityTask": PriorityTask}

    def __init__(self, data_file='data/tasks.json'):
        self.data_file = data_file
        # os.path.join keeps an absolute path as-is (handy for tests)
        self._data_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..', self.data_file
        )

    def load_tasks(self):
        """Loads tasks from JSON, rebuilding the right subclass from the '_type' field."""
        if not os.path.exists(self._data_file_path):
            os.makedirs(os.path.dirname(self._data_file_path), exist_ok=True)
            return []
        try:
            with open(self._data_file_path, 'r', encoding='utf-8') as f:
                raw_tasks = json.load(f)

            loaded = []
            for t_dict in raw_tasks:
                task_type = t_dict.pop('_type', 'Task')
                t_dict.setdefault('tags', [])
                cls = self.TYPE_MAP.get(task_type)
                if cls is None:
                    print(f"Warning: Unknown task type '{task_type}'. "
                          f"Skipping task ID {t_dict.get('id', 'N/A')}.")
                    continue
                loaded.append(cls(**t_dict))
            return loaded
        except json.JSONDecodeError:
            print("Warning: tasks.json is empty or corrupted. Starting with an empty task list.")
            return []
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"An unexpected error occurred during task loading: {e}. Starting with an empty list.")
            return []

    def save_tasks(self, tasks):
        """Saves tasks using each task's to_dict() (polymorphism)."""
        os.makedirs(os.path.dirname(self._data_file_path), exist_ok=True)
        with open(self._data_file_path, 'w', encoding='utf-8') as f:
            json.dump([t.to_dict() for t in tasks], f, indent=4, ensure_ascii=False)
