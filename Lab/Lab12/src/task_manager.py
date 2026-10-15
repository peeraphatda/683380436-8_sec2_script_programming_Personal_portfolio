"""Business logic: add, list, complete, delete, search, filter, sort."""
import datetime
import logging

from .task import Task, DueDateTask, PriorityTask
from .data_persistence import DataPersistence

logger = logging.getLogger(__name__)


class TaskManager:
    """Manages a collection of Task objects."""

    PRIORITY_MAP = {"High": 1, "Medium": 2, "Low": 3}

    def __init__(self, data_file="data/tasks.json"):
        self.persistence = DataPersistence(data_file)
        self.tasks = self.persistence.load_tasks()
        self.next_id = self._get_next_task_id()

    # ---------- helpers ----------
    def _get_next_task_id(self):
        return max((t.id for t in self.tasks), default=0) + 1

    def _save_changes(self):
        self.persistence.save_tasks(self.tasks)

    def _register(self, task):
        self.tasks.append(task)
        self.next_id += 1
        self._save_changes()
        logger.info("Task added: %r", task)
        return task

    # ---------- CRUD ----------
    def add_normal_task(self, description, tags=None):
        return self._register(Task(self.next_id, description, tags=tags))

    def add_due_date_task(self, description, due_date, tags=None):
        try:
            task = DueDateTask(self.next_id, description, due_date, tags=tags)
        except (ValueError, TypeError):
            logger.error("Invalid due date: %r", due_date)
            return None
        return self._register(task)

    def add_priority_task(self, description, priority, tags=None):
        try:
            task = PriorityTask(self.next_id, description, priority, tags=tags)
        except ValueError:
            logger.error("Invalid priority: %r", priority)
            return None
        return self._register(task)

    def get_task_by_id(self, task_id):
        return next((t for t in self.tasks if t.id == task_id), None)

    def get_all_tasks(self):
        return list(self.tasks)

    def complete_task(self, task_id):
        task = self.get_task_by_id(task_id)
        if task is None:
            return False, "Task not found."
        if task.completed:
            return False, "Task is already completed."
        task.mark_complete()
        self._save_changes()
        return True, "Task marked as completed."

    def delete_task(self, task_id):
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        if len(self.tasks) < before:
            self._save_changes()
            return True, "Task deleted successfully."
        return False, "Task not found."

    def add_tag_to_task(self, task_id, tag):
        task = self.get_task_by_id(task_id)
        if task is None:
            return False, "Task not found."
        task.add_tag(tag)
        self._save_changes()
        return True, "Tag added."

    def remove_tag_from_task(self, task_id, tag):
        task = self.get_task_by_id(task_id)
        if task is None:
            return False, "Task not found."
        task.remove_tag(tag)
        self._save_changes()
        return True, "Tag removed."

    # ---------- search ----------
    def search_tasks(self, keyword):
        """Case-insensitive partial match on description or tags."""
        if not keyword or not keyword.strip():
            return []
        kw = keyword.strip().lower()
        return [t for t in self.tasks
                if kw in t.description.lower() or any(kw in tag for tag in t.tags)]

    # ---------- filter ----------
    def filter_tasks(self, status=None, due_date_before=None, due_date_after=None,
                     priority_level=None, contains_tags=None):
        """
        Combine criteria with AND.
          status: True = completed, False = pending
          due_date_before / due_date_after: datetime.date (inclusive), DueDateTask only
          priority_level: 'High' | 'Medium' | 'Low', PriorityTask only
          contains_tags: list of tags; task must have ALL of them
        """
        result = list(self.tasks)
        if status is not None:
            result = [t for t in result if t.completed == status]
        if due_date_before:
            result = [t for t in result
                      if isinstance(t, DueDateTask) and t.due_date <= due_date_before]
        if due_date_after:
            result = [t for t in result
                      if isinstance(t, DueDateTask) and t.due_date >= due_date_after]
        if priority_level:
            result = [t for t in result
                      if isinstance(t, PriorityTask) and t.priority == priority_level]
        if contains_tags:
            wanted = [tag.strip().lower() for tag in contains_tags if tag.strip()]
            result = [t for t in result if all(w in t.tags for w in wanted)]
        return result

    # ---------- sort ----------
    def sort_tasks(self, criterion="id", reverse=False):
        """
        Sort by 'id' (default), 'description', 'completed', 'due_date', 'priority'.
        Tasks lacking a due date / priority are placed LAST in ascending order.
        """
        tasks = list(self.tasks)
        if criterion == "description":
            key = lambda t: (t.description.lower(), t.id)
        elif criterion == "completed":
            key = lambda t: (t.completed, t.id)
        elif criterion == "due_date":
            key = lambda t: (t.due_date if isinstance(t, DueDateTask)
                             else datetime.date.max, t.id)
        elif criterion == "priority":
            key = lambda t: (self.PRIORITY_MAP.get(getattr(t, "priority", None), 99), t.id)
        else:
            if criterion != "id":
                logger.warning("Unknown sort criterion '%s'; sorting by id.", criterion)
            key = lambda t: t.id
        return sorted(tasks, key=key, reverse=reverse)
