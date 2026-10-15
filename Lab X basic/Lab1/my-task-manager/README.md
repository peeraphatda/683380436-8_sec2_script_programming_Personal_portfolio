# My Simple Task Manager CLI

A lightweight, fully functional Command-Line Interface (CLI) application for managing daily tasks, written in Python with automatic JSON data persistence.

---

## 📋 Features

- **Add Tasks**: Create new tasks with a custom description.
- **List Tasks**: View all active and completed tasks with their corresponding IDs and statuses.
- **Complete Tasks**: Mark pending tasks as completed by ID.
- **Delete Tasks**: Remove unwanted tasks by ID.
- **Data Persistence**: Tasks are automatically saved to `data/tasks.json` upon exit and restored on startup.

---

## 📁 Project Structure

```text
my-task-manager/
├── src/
│   ├── __init__.py      # Package initializer
│   ├── task_data.py     # JSON file I/O operations (Load/Save)
│   └── task_logic.py    # Core business logic (Add, List, Complete, Delete)
├── data/
│   └── tasks.json       # Task database (Auto-generated)
├── main.py              # Application entry point
├── .gitignore           # Git ignore list
└── README.md            # Project documentation