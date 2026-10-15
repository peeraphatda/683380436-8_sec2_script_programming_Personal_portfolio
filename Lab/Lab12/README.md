# Final Project: Enhanced Task Manager CLI

A complete command-line task manager that applies OOP, modular design, data
persistence (JSON), `datetime` handling, error handling, and unit testing.

## Implemented Features

* **Task types**: normal `Task`, `DueDateTask` (with `due_date`), `PriorityTask` (High/Medium/Low).
* **Tags**: any task can have multiple tags (normalized to lowercase, no duplicates); add/remove tags later from the menu.
* **CRUD**: add, list, complete, delete tasks.
* **Search**: case-insensitive, partial match on description **and** tags.
* **Filter** (criteria combine with AND): completion status, due date before/after (inclusive), priority level, tasks containing ALL given tags.
* **Sort**: by `id` (default), `description`, `completed`, `due_date`, `priority`; ascending or descending. Tasks without a due date / priority are placed last.
* **Persistence**: tasks auto-save to `data/tasks.json` and load on startup. Corrupted/old files (e.g. without `tags`) are handled gracefully.
* **Logging**: uses Python's `logging` module (set level in `main.py`).

## How to Run

```bash
git clone https://github.com/YOUR_USERNAME/final_task_manager_project.git
cd final_task_manager_project
python main.py
```

Requires Python 3.8+ (no third-party packages).

## Run the Tests

```bash
python -m unittest discover -s tests -t . -v
```

## Project Structure

```
final_task_manager_project/
├── data/
│   └── tasks.json            # Stores tasks (sample data included for demo)
├── src/
│   ├── __init__.py           # Makes 'src' a package
│   ├── cli_interface.py      # User interaction (menus, input validation, output)
│   ├── data_persistence.py   # JSON load/save
│   ├── task.py               # Task, DueDateTask, PriorityTask (with tags)
│   └── task_manager.py       # Business logic (CRUD, search, filter, sort)
├── tests/
│   ├── __init__.py
│   └── test_task_manager.py  # Unit tests
├── .gitignore
├── main.py                   # Application entry point
├── PLAN.md                   # Plan, implementation notes, reflections
├── README.md                 # This file
└── SUBMISSION_CHECKLIST.md   # Final submission checklist
```

## Known Issues / Limitations

* Tasks cannot be edited after creation except for tags (no "edit description" yet).
* Tag/priority/date filters in the CLI ignore invalid input instead of re-prompting.
* Not designed for concurrent access to `tasks.json`.

## Future Work

* GUI (Tkinter / PyQt) or web interface (Flask / Django)
* SQLite database instead of JSON
* Reminders for upcoming due dates
* User accounts, recurring tasks, CSV/PDF export
