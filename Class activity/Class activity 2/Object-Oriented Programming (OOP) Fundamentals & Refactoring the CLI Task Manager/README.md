# My OOP Task Manager CLI

A command-line task manager built with Object-Oriented Programming (`Task` and `TaskManager` classes).

## Features
- Add, list, complete and delete tasks
- Persistence: tasks are saved to `data/tasks.json` and loaded on startup

## How to Run
```bash
git clone https://github.com/YOUR_USERNAME/my-oop-task-manager.git
cd my-oop-task-manager
python main.py
```

## Run tests
```bash
python -m unittest discover tests
```

## Project Structure
```
my-oop-task-manager/
├── src/
│   ├── __init__.py
│   ├── task.py            # Task class
│   └── task_manager.py    # TaskManager class (logic + persistence)
├── tests/
├── data/tasks.json        # created automatically
├── main.py                # CLI entry point
├── .gitignore
└── README.md
```
