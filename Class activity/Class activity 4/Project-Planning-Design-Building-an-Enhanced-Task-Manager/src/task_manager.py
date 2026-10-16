# src/task_manager.py
# Business logic only: no print() / input() and no direct file I/O here.
import datetime
from .task import Task, DueDateTask, PriorityTask
from .data_persistence import DataPersistence

# ลำดับความสำคัญ: เลขน้อย = สำคัญกว่า
PRIORITY_ORDER = {"high": 1, "medium": 2, "low": 3}


def _to_date(value):
    """แปลง 'YYYY-MM-DD' (หรือ date) เป็น datetime.date; ถ้าเป็น None คืน None"""
    if value is None or value == "":
        return None
    if isinstance(value, datetime.date):
        return value
    return datetime.datetime.strptime(value, "%Y-%m-%d").date()  # ValueError ถ้ารูปแบบผิด


class TaskManager:
    """Manages the collection of Task objects: add, list, complete, delete, search, filter, sort."""

    def __init__(self, data_file='data/tasks.json'):
        self.persistence = DataPersistence(data_file)
        self.tasks = self.persistence.load_tasks()
        self.next_id = self._get_next_task_id()

    # ---------- internal helpers ----------
    def _get_next_task_id(self):
        return 1 if not self.tasks else max(t.id for t in self.tasks) + 1

    def _save_changes(self):
        self.persistence.save_tasks(self.tasks)

    # ---------- CRUD ----------
    def add_normal_task(self, description, tags=None):
        task = Task(self.next_id, description, tags=tags)
        return self._add(task)

    def add_due_date_task(self, description, due_date_str, tags=None):
        task = DueDateTask(self.next_id, description, due_date_str, tags=tags)
        return self._add(task)

    def add_priority_task(self, description, priority, tags=None):
        task = PriorityTask(self.next_id, description, priority, tags=tags)
        return self._add(task)

    def _add(self, task):
        self.tasks.append(task)
        self.next_id += 1
        self._save_changes()
        return task

    def get_task_by_id(self, task_id):
        return next((t for t in self.tasks if t.id == task_id), None)

    def complete_task(self, task_id):
        task = self.get_task_by_id(task_id)
        if not task:
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

    def get_all_tasks(self):
        return list(self.tasks)

    # ---------- ASSIGNMENT: Search ----------
    def search_tasks(self, keyword):
        """ค้นหางานจากคำในคำอธิบาย (description) หรือ tags (ไม่สนตัวพิมพ์เล็ก/ใหญ่)"""
        kw = (keyword or "").strip().lower()
        if not kw:
            return []
        return [
            t for t in self.tasks
            if kw in t.description.lower() or any(kw in tag.lower() for tag in t.tags)
        ]

    # ---------- ASSIGNMENT: Filter ----------
    def filter_tasks(self, status=None, due_before=None, due_after=None, priority=None, tag=None):
        """
        กรองงานด้วยเงื่อนไขหลายแบบ (เงื่อนไขที่ไม่ใส่ = ไม่กรอง, ทุกเงื่อนไขใช้พร้อมกันแบบ AND)
          status     : True = เสร็จแล้ว, False = ยังไม่เสร็จ, None = ทั้งหมด
          due_before : เอางานที่ครบกำหนด <= วันนี้ (เฉพาะ DueDateTask)
          due_after  : เอางานที่ครบกำหนด >= วันนี้ (เฉพาะ DueDateTask)
          priority   : 'High' / 'Medium' / 'Low' (เฉพาะ PriorityTask)
          tag        : ชื่อ tag ที่ต้องมี
        """
        before = _to_date(due_before)
        after = _to_date(due_after)
        result = list(self.tasks)

        if status is not None:
            result = [t for t in result if t.completed == status]
        if before:
            result = [t for t in result if isinstance(t, DueDateTask) and t.due_date <= before]
        if after:
            result = [t for t in result if isinstance(t, DueDateTask) and t.due_date >= after]
        if priority:
            result = [t for t in result
                      if isinstance(t, PriorityTask) and t.priority.lower() == priority.lower()]
        if tag:
            result = [t for t in result if tag.lower() in (x.lower() for x in t.tags)]
        return result

    # ---------- ASSIGNMENT: Sort ----------
    def sort_tasks(self, criterion="id", reverse=False):
        """
        เรียงงานตาม: id | due_date | priority | status | description
        งานที่ไม่มีค่านั้น (เช่น ไม่มี due_date) จะอยู่ท้ายสุดเสมอ ไม่ว่าจะ reverse หรือไม่
        priority: ปกติ High -> Medium -> Low
        """
        if criterion == "id":
            return sorted(self.tasks, key=lambda t: t.id, reverse=reverse)
        if criterion == "status":  # ยังไม่เสร็จขึ้นก่อน
            return sorted(self.tasks, key=lambda t: (t.completed, t.id), reverse=reverse)
        if criterion == "description":
            return sorted(self.tasks, key=lambda t: t.description.lower(), reverse=reverse)

        if criterion == "due_date":
            has = lambda t: isinstance(t, DueDateTask)
            key = lambda t: t.due_date
        elif criterion == "priority":
            has = lambda t: isinstance(t, PriorityTask)
            key = lambda t: PRIORITY_ORDER.get(t.priority.lower(), 99)
        else:
            raise ValueError(f"Unknown sort criterion: {criterion}")

        with_value = sorted([t for t in self.tasks if has(t)], key=key, reverse=reverse)
        without_value = [t for t in self.tasks if not has(t)]
        return with_value + without_value
