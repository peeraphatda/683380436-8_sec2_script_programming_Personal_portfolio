# My Simple Task Manager CLI

A command-line application for managing daily tasks, built for Week 7
(CLI Application, Error Handling & Project Structure).

## Features
* **Add New Task** with a description and priority (High / Medium / Low)
* **List All / Pending / Completed Tasks** with a completion summary
* **Search Tasks by Keyword**
* **Mark Task as Completed** / **Delete Task** by ID
* **Persistence**: tasks are saved to `data/tasks.json` on exit and loaded on start
* **Defensive input**: invalid menu choices and non-numeric IDs are handled with `try-except`

## How to Run
```bash
git clone https://github.com/YOUR_USERNAME/my-task-manager.git
cd my-task-manager
python main.py
```

## Project Structure
```
my-task-manager/
├── src/
│   ├── __init__.py     # Makes 'src' a Python package
│   ├── task_data.py    # Persistence layer (JSON load/save)
│   └── task_logic.py   # Business logic (add, list, complete, delete, search)
├── data/
│   └── tasks.json      # Task storage (auto-managed)
├── main.py             # Presentation layer (CLI menu)
├── .gitignore
└── README.md
```
