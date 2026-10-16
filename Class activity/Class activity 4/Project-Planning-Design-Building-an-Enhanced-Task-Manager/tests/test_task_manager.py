# Run from project root:  python -m unittest discover -s tests -v
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.task_manager import TaskManager
from src.task import DueDateTask, PriorityTask


class TaskManagerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "tasks.json")  # absolute path
        self.m = TaskManager(self.path)
        self.m.add_normal_task("Read PLAN.md", tags=["study", "week11"])           # 1
        self.m.add_due_date_task("Submit project", "2026-09-30", tags=["school"])  # 2
        self.m.add_priority_task("Implement search", "High", tags=["python"])      # 3
        self.m.add_priority_task("Review JSON", "Low", tags=["python", "review"])  # 4
        self.m.add_due_date_task("Old task", "2021-12-30")                         # 5
        self.m.complete_task(1)

    def tearDown(self):
        self.tmp.cleanup()

    def ids(self, tasks):
        return [t.id for t in tasks]

    # --- search ---
    def test_search_description_and_tags_case_insensitive(self):
        self.assertEqual(self.ids(self.m.search_tasks("PYTHON")), [3, 4])
        self.assertEqual(self.ids(self.m.search_tasks("submit")), [2])
        self.assertEqual(self.m.search_tasks("nothing-here"), [])
        self.assertEqual(self.m.search_tasks("   "), [])

    # --- filter ---
    def test_filter_status(self):
        self.assertEqual(self.ids(self.m.filter_tasks(status=True)), [1])
        self.assertEqual(self.ids(self.m.filter_tasks(status=False)), [2, 3, 4, 5])

    def test_filter_due_range(self):
        self.assertEqual(self.ids(self.m.filter_tasks(due_before="2025-01-01")), [5])
        self.assertEqual(self.ids(self.m.filter_tasks(due_after="2026-01-01")), [2])
        self.assertEqual(self.ids(self.m.filter_tasks(due_after="2021-01-01", due_before="2027-01-01")), [2, 5])

    def test_filter_priority_and_tag_combined(self):
        self.assertEqual(self.ids(self.m.filter_tasks(priority="high")), [3])
        self.assertEqual(self.ids(self.m.filter_tasks(tag="python")), [3, 4])
        self.assertEqual(self.ids(self.m.filter_tasks(tag="python", priority="Low")), [4])
        self.assertEqual(self.ids(self.m.filter_tasks()), [1, 2, 3, 4, 5])

    # --- sort ---
    def test_sort_due_date_puts_missing_last(self):
        self.assertEqual(self.ids(self.m.sort_tasks("due_date")), [5, 2, 1, 3, 4])
        self.assertEqual(self.ids(self.m.sort_tasks("due_date", reverse=True)), [2, 5, 1, 3, 4])

    def test_sort_priority_high_first(self):
        self.assertEqual(self.ids(self.m.sort_tasks("priority")), [3, 4, 1, 2, 5])

    def test_sort_id_and_invalid(self):
        self.assertEqual(self.ids(self.m.sort_tasks("id", reverse=True)), [5, 4, 3, 2, 1])
        with self.assertRaises(ValueError):
            self.m.sort_tasks("bogus")

    # --- persistence ---
    def test_save_and_reload_keeps_types(self):
        m2 = TaskManager(self.path)
        self.assertEqual(len(m2.tasks), 5)
        self.assertIsInstance(m2.get_task_by_id(2), DueDateTask)
        self.assertIsInstance(m2.get_task_by_id(3), PriorityTask)
        self.assertEqual(m2.next_id, 6)

    def test_delete_and_complete_messages(self):
        self.assertEqual(self.m.complete_task(1)[0], False)   # already completed
        self.assertEqual(self.m.complete_task(99)[0], False)  # not found
        self.assertEqual(self.m.delete_task(5)[0], True)
        self.assertEqual(self.m.delete_task(5)[0], False)


if __name__ == "__main__":
    unittest.main()
