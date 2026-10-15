"""Unit tests for Task models and TaskManager (search / filter / sort)."""
import datetime
import json
import os
import tempfile
import unittest

from src.task import Task, DueDateTask, PriorityTask
from src.task_manager import TaskManager


class TestTaskModels(unittest.TestCase):
    def test_tags_default_empty_list(self):
        self.assertEqual(Task(1, "a").tags, [])

    def test_tags_not_shared_between_instances(self):
        a, b = Task(1, "a"), Task(2, "b")
        a.add_tag("x")
        self.assertEqual(b.tags, [])

    def test_add_tag_normalizes_and_prevents_duplicates(self):
        t = Task(1, "a")
        t.add_tag("  Work ")
        t.add_tag("work")
        t.add_tag("   ")
        self.assertEqual(t.tags, ["work"])

    def test_remove_tag(self):
        t = Task(1, "a", tags=["x", "y"])
        t.remove_tag("X")
        t.remove_tag("missing")  # no error
        self.assertEqual(t.tags, ["y"])

    def test_due_date_string_and_invalid(self):
        t = DueDateTask(1, "a", "2026-01-02")
        self.assertEqual(t.due_date, datetime.date(2026, 1, 2))
        with self.assertRaises(ValueError):
            DueDateTask(2, "b", "02/01/2026")
        with self.assertRaises(TypeError):
            DueDateTask(3, "c", 12345)

    def test_invalid_priority(self):
        with self.assertRaises(ValueError):
            PriorityTask(1, "a", "Urgent")

    def test_to_dict_types_and_tags(self):
        self.assertEqual(Task(1, "a", tags=["x"]).to_dict()["_type"], "Task")
        d = DueDateTask(1, "a", "2026-01-02", tags=["x"]).to_dict()
        self.assertEqual((d["_type"], d["due_date"], d["tags"]),
                         ("DueDateTask", "2026-01-02", ["x"]))
        self.assertEqual(PriorityTask(1, "a", "High").to_dict()["priority"], "High")

    def test_str_contains_extras_and_tags(self):
        s = str(DueDateTask(1, "a", "2026-01-02", tags=["x"]))
        self.assertIn("Due: 2026-01-02", s)
        self.assertIn("Tags: x", s)
        self.assertLess(s.index("Due:"), s.index("Tags:"))


class ManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "tasks.json")
        self.m = TaskManager(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def populate(self):
        self.m.add_normal_task("Buy Groceries", ["home", "shopping"])            # 1
        self.m.add_due_date_task("Submit project", "2026-10-20", ["school", "urgent"])  # 2
        self.m.add_priority_task("Prepare slides", "High", ["school"])           # 3
        self.m.add_priority_task("Read docs", "Low", ["study"])                  # 4
        self.m.add_due_date_task("Pay bill", "2026-10-15", ["home", "urgent"])   # 5
        self.m.complete_task(4)


class TestCRUDAndPersistence(ManagerTestCase):
    def test_empty_start(self):
        self.assertEqual(self.m.get_all_tasks(), [])
        self.assertEqual(self.m.next_id, 1)

    def test_add_complete_delete(self):
        t = self.m.add_normal_task("x")
        self.assertEqual(t.id, 1)
        self.assertEqual(self.m.complete_task(1), (True, "Task marked as completed."))
        self.assertFalse(self.m.complete_task(1)[0])
        self.assertFalse(self.m.complete_task(99)[0])
        self.assertTrue(self.m.delete_task(1)[0])
        self.assertFalse(self.m.delete_task(1)[0])

    def test_invalid_inputs_return_none(self):
        self.assertIsNone(self.m.add_due_date_task("x", "not-a-date"))
        self.assertIsNone(self.m.add_priority_task("x", "Urgent"))
        self.assertEqual(self.m.get_all_tasks(), [])

    def test_ids_not_reused_after_delete_of_middle(self):
        self.populate()
        self.m.delete_task(2)
        self.assertEqual(self.m.add_normal_task("new").id, 6)

    def test_persistence_round_trip(self):
        self.populate()
        m2 = TaskManager(self.path)
        self.assertEqual([t.to_dict() for t in m2.tasks],
                         [t.to_dict() for t in self.m.tasks])
        self.assertIsInstance(m2.get_task_by_id(2), DueDateTask)
        self.assertIsInstance(m2.get_task_by_id(3), PriorityTask)
        self.assertEqual(m2.next_id, 6)

    def test_load_old_data_without_tags(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([{"id": 1, "description": "old", "completed": False}], f)
        self.assertEqual(TaskManager(self.path).tasks[0].tags, [])

    def test_corrupted_file_gives_empty_list(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("{not json")
        self.assertEqual(TaskManager(self.path).tasks, [])

    def test_tag_management(self):
        self.populate()
        self.m.add_tag_to_task(1, "NEW")
        self.assertIn("new", self.m.get_task_by_id(1).tags)
        self.m.remove_tag_from_task(1, "new")
        self.assertNotIn("new", self.m.get_task_by_id(1).tags)
        self.assertFalse(self.m.add_tag_to_task(99, "x")[0])


class TestSearch(ManagerTestCase):
    def test_case_insensitive_description(self):
        self.populate()
        self.assertEqual([t.id for t in self.m.search_tasks("GROCER")], [1])

    def test_search_in_tags_partial(self):
        self.populate()
        self.assertEqual([t.id for t in self.m.search_tasks("urg")], [2, 5])

    def test_empty_and_no_match(self):
        self.populate()
        self.assertEqual(self.m.search_tasks(""), [])
        self.assertEqual(self.m.search_tasks("   "), [])
        self.assertEqual(self.m.search_tasks("zzz"), [])


class TestFilter(ManagerTestCase):
    def test_no_criteria_returns_all(self):
        self.populate()
        self.assertEqual(len(self.m.filter_tasks()), 5)

    def test_status(self):
        self.populate()
        self.assertEqual([t.id for t in self.m.filter_tasks(status=True)], [4])
        self.assertEqual(len(self.m.filter_tasks(status=False)), 4)

    def test_due_date_range_inclusive(self):
        self.populate()
        d = datetime.date
        self.assertEqual([t.id for t in self.m.filter_tasks(due_date_before=d(2026, 10, 15))], [5])
        self.assertEqual([t.id for t in self.m.filter_tasks(due_date_after=d(2026, 10, 20))], [2])
        self.assertEqual(
            sorted(t.id for t in self.m.filter_tasks(due_date_after=d(2026, 10, 1),
                                                     due_date_before=d(2026, 10, 31))),
            [2, 5])

    def test_priority(self):
        self.populate()
        self.assertEqual([t.id for t in self.m.filter_tasks(priority_level="High")], [3])

    def test_tags_require_all(self):
        self.populate()
        self.assertEqual([t.id for t in self.m.filter_tasks(contains_tags=["home", "urgent"])], [5])
        self.assertEqual(self.m.filter_tasks(contains_tags=["home", "school"]), [])

    def test_combined_criteria(self):
        self.populate()
        result = self.m.filter_tasks(status=False, contains_tags=["urgent"],
                                     due_date_before=datetime.date(2026, 10, 16))
        self.assertEqual([t.id for t in result], [5])


class TestSort(ManagerTestCase):
    def test_default_id(self):
        self.populate()
        self.assertEqual([t.id for t in self.m.sort_tasks()], [1, 2, 3, 4, 5])
        self.assertEqual([t.id for t in self.m.sort_tasks("id", True)], [5, 4, 3, 2, 1])

    def test_due_date_missing_last(self):
        self.populate()
        self.assertEqual([t.id for t in self.m.sort_tasks("due_date")], [5, 2, 1, 3, 4])

    def test_priority_mapping(self):
        self.populate()
        self.assertEqual([t.id for t in self.m.sort_tasks("priority")], [3, 4, 1, 2, 5])

    def test_description_case_insensitive(self):
        self.populate()
        descs = [t.description for t in self.m.sort_tasks("description")]
        self.assertEqual(descs, sorted(descs, key=str.lower))

    def test_completed(self):
        self.populate()
        self.assertEqual(self.m.sort_tasks("completed")[-1].id, 4)

    def test_unknown_criterion_falls_back_to_id(self):
        self.populate()
        self.assertEqual([t.id for t in self.m.sort_tasks("bogus")], [1, 2, 3, 4, 5])

    def test_sort_does_not_mutate_original_order(self):
        self.populate()
        self.m.sort_tasks("priority", True)
        self.assertEqual([t.id for t in self.m.tasks], [1, 2, 3, 4, 5])


if __name__ == "__main__":
    unittest.main()
