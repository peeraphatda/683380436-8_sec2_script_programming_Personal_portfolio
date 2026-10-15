import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import task_data
import task_logic

def display_menu():
    print("\n--- Task Manager Menu ---")
    print("1. Add Task")
    print("2. List Tasks")
    print("3. Complete Task")
    print("4. Delete Task")
    print("5. Exit")
    print("-------------------------")

def main():
    tasks = task_data.load_tasks()
    while True:
        display_menu()
        choice = input("Enter choice (1-5): ").strip()
        if choice == '1':
            desc = input("Task description: ").strip()
            if desc: 
                tasks = task_logic.add_task(tasks, desc)
        elif choice == '2':
            task_logic.list_tasks(tasks)
        elif choice == '3':
            try:
                tid = int(input("Task ID to complete: ").strip())
                tasks = task_logic.complete_task(tasks, tid)
            except ValueError: 
                print("Invalid ID.")
        elif choice == '4':
            try:
                tid = int(input("Task ID to delete: ").strip())
                tasks = task_logic.delete_task(tasks, tid)
            except ValueError: 
                print("Invalid ID.")
        elif choice == '5':
            task_data.save_tasks(tasks)
            print("Saved and exiting. Goodbye!")
            break

if __name__ == "__main__":
    main()