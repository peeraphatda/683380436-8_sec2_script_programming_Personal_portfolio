"""Command-line interface. Contains no business logic; delegates to TaskManager."""
import datetime

PRIORITIES = ["High", "Medium", "Low"]


class CLIInterface:
    def __init__(self, task_manager):
        self.manager = task_manager

    # ---------- display ----------
    def display_menu(self):
        print("\n--- Enhanced Task Manager Menu ---")
        print("1. Add Normal Task")
        print("2. Add Due Date Task")
        print("3. Add Priority Task")
        print("4. List All Tasks")
        print("5. Complete Task")
        print("6. Delete Task")
        print("7. Search Tasks")
        print("8. Filter Tasks")
        print("9. Sort Tasks")
        print("10. Add/Remove Tag on a Task")
        print("0. Exit")
        print("----------------------------------")

    def _display_tasks(self, tasks, title="Tasks"):
        if not tasks:
            print(f"No {title.lower()} found.")
            return
        print(f"\n--- {title} ---")
        for task in tasks:
            print(task)
        print("------------------")

    # ---------- input helpers ----------
    def get_user_choice(self):
        return input("Enter your choice (0-10): ").strip()

    def get_task_description(self):
        while True:
            description = input("Enter task description: ").strip()
            if description:
                return description
            print("Task description cannot be empty. Please try again.")

    def get_due_date_input(self):
        while True:
            value = input("Enter due date (YYYY-MM-DD): ").strip()
            try:
                datetime.datetime.strptime(value, "%Y-%m-%d")
                return value
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD (e.g., 2026-12-31).")

    def get_priority_input(self):
        while True:
            priority = input("Enter priority (High/Medium/Low): ").strip().capitalize()
            if priority in PRIORITIES:
                return priority
            print("Invalid priority. Please enter 'High', 'Medium', or 'Low'.")

    def get_tags_input(self):
        raw = input("Enter tags (comma-separated, e.g., work,urgent - optional): ").strip()
        return [t.strip().lower() for t in raw.split(",") if t.strip()]

    def _get_task_id(self, action):
        try:
            return int(input(f"Enter ID of task to {action}: ").strip())
        except ValueError:
            print("Invalid input. Please enter a number for Task ID.")
            return None

    def _optional_date(self, prompt):
        raw = input(prompt).strip()
        if not raw:
            return None
        try:
            return datetime.datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Ignoring this filter.")
            return None

    # ---------- actions ----------
    def _add_normal(self):
        task = self.manager.add_normal_task(self.get_task_description(), self.get_tags_input())
        print(f"Normal Task '{task.description}' added with ID {task.id}.")

    def _add_due(self):
        desc = self.get_task_description()
        due = self.get_due_date_input()
        task = self.manager.add_due_date_task(desc, due, self.get_tags_input())
        if task:
            print(f"Due Date Task '{task.description}' (Due: {task.due_date}) added with ID {task.id}.")
        else:
            print("Failed to add Due Date Task. Please check your input.")

    def _add_priority(self):
        desc = self.get_task_description()
        prio = self.get_priority_input()
        task = self.manager.add_priority_task(desc, prio, self.get_tags_input())
        if task:
            print(f"Priority Task '{task.description}' (Priority: {task.priority}) added with ID {task.id}.")
        else:
            print("Failed to add Priority Task. Please check your input.")

    def _complete(self):
        task_id = self._get_task_id("complete")
        if task_id is not None:
            print(self.manager.complete_task(task_id)[1])

    def _delete(self):
        task_id = self._get_task_id("delete")
        if task_id is not None:
            print(self.manager.delete_task(task_id)[1])

    def _search(self):
        keyword = input("Enter search keyword (in description or tags): ").strip()
        self._display_tasks(self.manager.search_tasks(keyword),
                            f"Search Results for '{keyword}'")

    def _filter(self):
        print("\n--- Filter Tasks (leave blank to skip a criterion) ---")
        status_in = input("Completed status (yes/no): ").strip().lower()
        status = True if status_in == "yes" else False if status_in == "no" else None
        before = self._optional_date("Due on or before (YYYY-MM-DD): ")
        after = self._optional_date("Due on or after (YYYY-MM-DD): ")
        prio_in = input("Priority (High/Medium/Low): ").strip().capitalize()
        priority = prio_in if prio_in in PRIORITIES else None
        tags_in = input("Tags (comma-separated, task must have ALL): ").strip()
        tags = [t.strip().lower() for t in tags_in.split(",") if t.strip()] or None
        results = self.manager.filter_tasks(status, before, after, priority, tags)
        self._display_tasks(results, "Filtered Tasks")

    def _sort(self):
        print("\n--- Sort Tasks ---")
        print("Available criteria: id, description, completed, due_date, priority")
        criterion = input("Sort by (default: id): ").strip().lower() or "id"
        reverse = input("Reverse order (yes/no, default: no): ").strip().lower() == "yes"
        order = "Descending" if reverse else "Ascending"
        self._display_tasks(self.manager.sort_tasks(criterion, reverse),
                            f"Sorted Tasks by {criterion} ({order})")

    def _manage_tag(self):
        task_id = self._get_task_id("modify tags on")
        if task_id is None:
            return
        action = input("Add or remove tag? (add/remove): ").strip().lower()
        tag = input("Tag: ").strip()
        if not tag:
            print("Tag cannot be empty.")
        elif action == "add":
            print(self.manager.add_tag_to_task(task_id, tag)[1])
        elif action == "remove":
            print(self.manager.remove_tag_from_task(task_id, tag)[1])
        else:
            print("Please type 'add' or 'remove'.")

    def run(self):
        actions = {
            "1": self._add_normal, "2": self._add_due, "3": self._add_priority,
            "4": lambda: self._display_tasks(self.manager.get_all_tasks(), "Your Tasks"),
            "5": self._complete, "6": self._delete, "7": self._search,
            "8": self._filter, "9": self._sort, "10": self._manage_tag,
        }
        while True:
            self.display_menu()
            choice = self.get_user_choice()
            if choice == "0":
                print("Exiting Task Manager. Goodbye!")
                break
            action = actions.get(choice)
            if action:
                action()
            else:
                print("Invalid choice. Please enter a number between 0 and 10.")
