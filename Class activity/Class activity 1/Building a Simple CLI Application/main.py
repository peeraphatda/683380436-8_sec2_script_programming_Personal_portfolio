# main.py - Presentation Layer (CLI Menu & Defensive Input)
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

import task_data
import task_logic


def display_menu():
    print("\n" + "=" * 32)
    print("        TASK MANAGER CLI")
    print("=" * 32)
    print("  1. Add New Task")
    print("  2. List All Tasks")
    print("  3. List Pending Tasks")
    print("  4. List Completed Tasks")
    print("  5. Search Tasks by Keyword")
    print("  6. Mark Task as Completed")
    print("  7. Delete Task")
    print("  8. Save and Exit")
    print("=" * 32)


def ask_task_id(prompt):
    """Asks for a task ID; returns int or None if input is invalid."""
    raw = input(prompt).strip()
    try:
        return int(raw)
    except ValueError:
        print("Invalid input. Please enter a number for Task ID.")
        return None


def ask_priority():
    print("Priority: 1. High  2. Medium  3. Low")
    choice = input("Select priority (1-3, default 2): ").strip()
    return task_logic.PRIORITIES.get(choice, "Medium")


def main():
    tasks = task_data.load_tasks()
    try:
        while True:
            display_menu()
            choice = input("Enter choice (1-8): ").strip()

            if choice == '1':
                description = input("Enter task description: ").strip()
                if description:
                    priority = ask_priority()
                    tasks = task_logic.add_task(tasks, description, priority)
                else:
                    print("Task description cannot be empty.")
            elif choice == '2':
                task_logic.list_tasks(tasks)
            elif choice == '3':
                task_logic.list_tasks(tasks, "pending")
            elif choice == '4':
                task_logic.list_tasks(tasks, "completed")
            elif choice == '5':
                keyword = input("Enter keyword to search: ").strip()
                if keyword:
                    task_logic.search_tasks(tasks, keyword)
                else:
                    print("Keyword cannot be empty.")
            elif choice == '6':
                task_id = ask_task_id("Enter ID of task to complete: ")
                if task_id is not None:
                    tasks = task_logic.complete_task(tasks, task_id)
            elif choice == '7':
                task_id = ask_task_id("Enter ID of task to delete: ")
                if task_id is not None:
                    tasks = task_logic.delete_task(tasks, task_id)
            elif choice == '8':
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 8.")
    except (KeyboardInterrupt, EOFError):
        print()
    finally:
        task_data.save_tasks(tasks)
        print("Tasks saved. Goodbye!")


if __name__ == "__main__":
    main()
