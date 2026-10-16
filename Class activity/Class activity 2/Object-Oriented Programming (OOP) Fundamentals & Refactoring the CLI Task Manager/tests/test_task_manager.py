import os
import tempfile
import unittest
from src.task_manager import TaskManager


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(tempfile.mkdtemp(), "t.json")
        # data_file is joined to project root; absolute path overrides the join
        self.m = TaskManager(data_file=self.path)

    def test_add_and_persist(self):
        self.m.add_task("one")
        self.assertEqual(len(TaskManager(data_file=self.path).tasks), 1)

    def test_complete(self):
        self.m.add_task("one")
        self.m.complete_task(1)
        self.assertTrue(self.m.tasks[0].completed)

    def test_delete(self):
        self.m.add_task("one")
        self.m.delete_task(1)
        self.assertEqual(self.m.tasks, [])

    def test_next_id_after_reload(self):
        self.m.add_task("one")
        self.m.add_task("two")
        self.assertEqual(TaskManager(data_file=self.path).next_id, 3)


if __name__ == "__main__":
    unittest.main()
