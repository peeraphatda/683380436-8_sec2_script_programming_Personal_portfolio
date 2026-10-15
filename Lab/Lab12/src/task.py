"""Task models: Task, DueDateTask, PriorityTask (all support tags)."""
import datetime


class Task:
    """Base class for all tasks. Includes a 'tags' list for categorization."""

    def __init__(self, id, description, completed=False, tags=None):
        self.id = id
        self.description = description
        self.completed = completed
        # Always a list of normalized (lowercase, stripped) strings
        self.tags = []
        for tag in (tags or []):
            self.add_tag(tag)

    def mark_complete(self):
        """Marks the task as completed."""
        self.completed = True

    def add_tag(self, tag):
        """Adds a tag, preventing duplicates and empty tags."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        """Removes a tag if present."""
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)

    def to_dict(self):
        """Converts the task to a JSON-serializable dict (with '_type')."""
        return {
            "id": self.id,
            "description": self.description,
            "completed": self.completed,
            "tags": list(self.tags),
            "_type": "Task",
        }

    def _tags_str(self):
        return f" | Tags: {', '.join(self.tags)}" if self.tags else ""

    def _extra_str(self):
        """Subclasses override to add their own field before the tags."""
        return ""

    def __str__(self):
        status = "Completed" if self.completed else "Pending"
        return (f"ID: {self.id} | Description: {self.description} | "
                f"Status: {status}{self._extra_str()}{self._tags_str()}")

    def __repr__(self):
        return (f"Task(id={self.id}, description='{self.description}', "
                f"completed={self.completed}, tags={self.tags})")


class DueDateTask(Task):
    """A task with a due date stored as a datetime.date."""

    def __init__(self, id, description, due_date, completed=False, tags=None):
        super().__init__(id, description, completed, tags)
        if isinstance(due_date, str):
            self.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
        elif isinstance(due_date, datetime.datetime):
            self.due_date = due_date.date()
        elif isinstance(due_date, datetime.date):
            self.due_date = due_date
        else:
            raise TypeError(
                "due_date must be a 'YYYY-MM-DD' string or a datetime.date object")

    def to_dict(self):
        data = super().to_dict()
        data["due_date"] = self.due_date.strftime("%Y-%m-%d")
        data["_type"] = "DueDateTask"
        return data

    def _extra_str(self):
        return f" | Due: {self.due_date.strftime('%Y-%m-%d')}"

    def __repr__(self):
        return (f"DueDateTask(id={self.id}, description='{self.description}', "
                f"due_date='{self.due_date}', completed={self.completed}, "
                f"tags={self.tags})")


class PriorityTask(Task):
    """A task with a priority level (High / Medium / Low)."""

    ALLOWED_PRIORITIES = ("High", "Medium", "Low")

    def __init__(self, id, description, priority, completed=False, tags=None):
        super().__init__(id, description, completed, tags)
        if priority not in self.ALLOWED_PRIORITIES:
            raise ValueError(
                f"Priority must be one of {list(self.ALLOWED_PRIORITIES)}")
        self.priority = priority

    def to_dict(self):
        data = super().to_dict()
        data["priority"] = self.priority
        data["_type"] = "PriorityTask"
        return data

    def _extra_str(self):
        return f" | Priority: {self.priority}"

    def __repr__(self):
        return (f"PriorityTask(id={self.id}, description='{self.description}', "
                f"priority='{self.priority}', completed={self.completed}, "
                f"tags={self.tags})")
