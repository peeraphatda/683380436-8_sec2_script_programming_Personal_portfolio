# src/task.py  (Data Models)
import datetime


class Task:
    """Base class for all tasks. Includes a 'tags' attribute."""

    def __init__(self, id, description, completed=False, tags=None):
        self.id = id
        self.description = description
        self.completed = completed
        self.tags = tags if tags is not None else []

    def mark_complete(self):
        """Marks the task as completed."""
        self.completed = True

    def add_tag(self, tag):
        """Adds a tag to the task (no duplicates)."""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        """Removes a tag from the task."""
        if tag in self.tags:
            self.tags.remove(tag)

    def to_dict(self):
        """Converts the Task to a dict for JSON serialization (with '_type')."""
        return {
            "id": self.id,
            "description": self.description,
            "completed": self.completed,
            "tags": self.tags,
            "_type": "Task",
        }

    def _tags_str(self):
        return f" | Tags: {', '.join(self.tags)}" if self.tags else ""

    def _base_str(self):
        status = "Completed" if self.completed else "Pending"
        return f"ID: {self.id} | Description: {self.description} | Status: {status}"

    def __str__(self):
        return f"{self._base_str()}{self._tags_str()}"

    def __repr__(self):
        return (f"Task(id={self.id}, description='{self.description}', "
                f"completed={self.completed}, tags={self.tags})")


class DueDateTask(Task):
    """A task with a due date (stored as datetime.date)."""

    def __init__(self, id, description, due_date, completed=False, tags=None):
        super().__init__(id, description, completed, tags)
        if isinstance(due_date, str):
            self.due_date = datetime.datetime.strptime(due_date, '%Y-%m-%d').date()
        elif isinstance(due_date, datetime.date):
            self.due_date = due_date
        else:
            raise TypeError("due_date must be a 'YYYY-MM-DD' string or a datetime.date object")

    def to_dict(self):
        d = super().to_dict()
        d["due_date"] = self.due_date.strftime('%Y-%m-%d')
        d["_type"] = "DueDateTask"
        return d

    def __str__(self):
        return f"{self._base_str()} | Due: {self.due_date.strftime('%Y-%m-%d')}{self._tags_str()}"

    def __repr__(self):
        return (f"DueDateTask(id={self.id}, description='{self.description}', "
                f"due_date='{self.due_date.strftime('%Y-%m-%d')}', "
                f"completed={self.completed}, tags={self.tags})")


class PriorityTask(Task):
    """A task with a priority level (High / Medium / Low)."""

    def __init__(self, id, description, priority, completed=False, tags=None):
        super().__init__(id, description, completed, tags)
        self.priority = priority

    def to_dict(self):
        d = super().to_dict()
        d["priority"] = self.priority
        d["_type"] = "PriorityTask"
        return d

    def __str__(self):
        return f"{self._base_str()} | Priority: {self.priority}{self._tags_str()}"

    def __repr__(self):
        return (f"PriorityTask(id={self.id}, description='{self.description}', "
                f"priority='{self.priority}', completed={self.completed}, tags={self.tags})")
