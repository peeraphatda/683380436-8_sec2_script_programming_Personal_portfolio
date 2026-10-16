# src/task_manager.py
import json
import os

from .task import Task


class TaskManager:
    """Manages the collection of Task objects: load, save, add, list, complete, delete."""

    def __init__(self, data_file="data/tasks.json"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.file_path = os.path.join(base_dir, data_file)
        self.tasks = self._load_tasks()
        self.next_id = self._get_next_task_id()

    def _get_next_task_id(self):
        if not self.tasks:
            return 1
        return max(task.id for task in self.tasks) + 1

    def _load_tasks(self):
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            return []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw_tasks = json.load(f)
            return [Task(t["id"], t["description"], t["completed"]) for t in raw_tasks]
        except json.JSONDecodeError:
            print("Warning: tasks.json is empty or corrupted. Starting with an empty task list.")
            return []

    def _save_tasks(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=4, ensure_ascii=False)

    def add_task(self, description):
        new_task = Task(self.next_id, description)
        self.tasks.append(new_task)
        self.next_id += 1
        self._save_tasks()
        print(f"Task '{description}' added with ID {new_task.id}.")

    def list_tasks(self):
        if not self.tasks:
            print("No tasks found.")
            return
        print("\n--- Your Tasks ---")
        for task in self.tasks:
            print(task)
        print("------------------")

    def complete_task(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                if task.completed:
                    print(f"Task ID {task_id} is already completed.")
                else:
                    task.mark_complete()
                    self._save_tasks()
                    print(f"Task ID {task_id} marked as completed.")
                return
        print(f"Error: Task with ID {task_id} not found.")

    def delete_task(self, task_id):
        original_len = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        if len(self.tasks) < original_len:
            self._save_tasks()
            print(f"Task ID {task_id} deleted successfully.")
        else:
            print(f"Error: Task with ID {task_id} not found.")
