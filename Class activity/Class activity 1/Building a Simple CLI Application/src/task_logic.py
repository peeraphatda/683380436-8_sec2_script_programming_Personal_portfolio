# src/task_logic.py - Business Logic Layer (Add, List, Complete, Delete, Search)

PRIORITIES = {"1": "High", "2": "Medium", "3": "Low"}
LINE = "=" * 66
THIN = "-" * 66


def get_next_task_id(tasks):
    """Generates a unique ID for a new task."""
    if not tasks:
        return 1
    return max(task['id'] for task in tasks) + 1


def add_task(tasks, description, priority="Medium"):
    """Adds a new task to the list."""
    task_id = get_next_task_id(tasks)
    tasks.append({
        "id": task_id,
        "description": description,
        "priority": priority,
        "completed": False
    })
    print(f"Task '{description}' added with ID {task_id} (Priority: {priority}).")
    return tasks


def _print_table(task_list):
    print("\n" + LINE)
    print(f"{'ID':<6} | {'Status':<12} | {'Priority':<10} | Description")
    print(THIN)
    for t in task_list:
        status = "[DONE]" if t['completed'] else "[PENDING]"
        print(f"{'#' + str(t['id']):<6} | {status:<12} | {t.get('priority', 'Medium'):<10} | {t['description']}")
    print(LINE)


def list_tasks(tasks, filter_status=None):
    """Lists tasks. filter_status: None (all), 'pending', or 'completed'."""
    if filter_status == "pending":
        shown = [t for t in tasks if not t['completed']]
    elif filter_status == "completed":
        shown = [t for t in tasks if t['completed']]
    else:
        shown = tasks

    if not shown:
        print("\nNo tasks found.")
        return

    _print_table(shown)
    done = sum(1 for t in tasks if t['completed'])
    print(f"Summary: {done}/{len(tasks)} task(s) completed.")


def search_tasks(tasks, keyword):
    """Searches tasks whose description contains the keyword (case-insensitive)."""
    results = [t for t in tasks if keyword.lower() in t['description'].lower()]
    if not results:
        print(f"\nNo tasks found matching '{keyword}'.")
        return
    _print_table(results)
    print(f"Found {len(results)} task(s) matching '{keyword}'.")


def complete_task(tasks, task_id):
    """Marks a task as completed."""
    for task in tasks:
        if task['id'] == task_id:
            if task['completed']:
                print(f"Task ID {task_id} is already completed.")
            else:
                task['completed'] = True
                print(f"Task ID {task_id} marked as completed.")
            return tasks
    print(f"Error: Task with ID {task_id} not found.")
    return tasks


def delete_task(tasks, task_id):
    """Deletes a task from the list."""
    original_len = len(tasks)
    tasks[:] = [t for t in tasks if t['id'] != task_id]
    if len(tasks) < original_len:
        print(f"Task ID {task_id} deleted successfully.")
    else:
        print(f"Error: Task with ID {task_id} not found.")
    return tasks
