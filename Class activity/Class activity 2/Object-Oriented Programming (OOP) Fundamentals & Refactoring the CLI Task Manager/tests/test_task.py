import unittest
from src.task import Task


class TestTask(unittest.TestCase):
    def test_defaults(self):
        self.assertFalse(Task(1, "a").completed)

    def test_mark_complete(self):
        t = Task(1, "a")
        t.mark_complete()
        self.assertTrue(t.completed)

    def test_to_dict(self):
        self.assertEqual(Task(1, "a").to_dict(), {"id": 1, "description": "a", "completed": False})

    def test_str(self):
        self.assertEqual(str(Task(2, "x", True)), "ID: 2 | Description: x | Status: Completed")


if __name__ == "__main__":
    unittest.main()
