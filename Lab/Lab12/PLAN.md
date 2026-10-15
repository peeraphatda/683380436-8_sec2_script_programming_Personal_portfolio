# Project Plan: Enhanced Task Manager CLI (Final Version)

## 1. Introduction
A modular, object-oriented command-line task manager. This document records
the plan, what was implemented, challenges, and final reflections.

## 2. Requirements

### 2.1 Functional (all implemented)
* **Task management**: create, list, complete, delete; `DueDateTask` and `PriorityTask` types.
* **Tags**: optional list of strings on every task; add/remove tag.
* **Search**: keyword in description or tags, case-insensitive, partial match.
* **Filter**: status, due-date range, priority, tags (ALL), combined with AND.
* **Sort**: id, description, completed, due date, priority (asc/desc).
* **Persistence**: JSON file `data/tasks.json`, loaded on start, saved on every change.

### 2.2 Non-functional
* **Usability**: clear menu, validated prompts, informative messages.
* **Reliability**: handles invalid input, missing/corrupted data file, old data without tags.
* **Maintainability**: separation of concerns, docstrings, PEP 8 style.
* **Extensibility**: new task types / filters / storage backends can be added with small changes.

## 3. Architecture

| Layer | Module | Responsibility |
|-------|--------|----------------|
| Model | `src/task.py` | Task classes, tags, `to_dict`, `__str__` |
| Data | `src/data_persistence.py` | JSON load/save, rebuild objects from `_type` |
| Logic | `src/task_manager.py` | CRUD, search, filter, sort |
| UI | `src/cli_interface.py` | Menus, input validation, output only |
| Entry | `main.py` | Wires manager + CLI together |
| Tests | `tests/test_task_manager.py` | Unit tests for models and manager |

## 4. Implementation Notes

* **Tags**: normalized (strip + lowercase) inside `Task.add_tag`; the constructor routes through it so loaded data is also normalized.
* **Search**: `keyword in description.lower()` or `any(keyword in tag ...)`.
* **Filter**: applied sequentially (AND). Date and priority filters use `isinstance` so only the relevant subclass matches.
* **Sort**: `sorted()` + lambda keys. Missing due date → `datetime.date.max`; priority mapped High=1, Medium=2, Low=3, missing=99; `id` is a tie-breaker so ordering is stable and deterministic.
* **Imports**: `main.py` imports `from src...` and modules use relative imports, so the package works when run from the project root (no `sys.path` hacks).
* **Logging**: `logging` replaces scattered debug prints.

## 5. Testing
32 unit tests cover models, persistence round-trip, corrupted/old data, search,
filter (single & combined), and sort (incl. missing attributes and unknown criteria).
Run: `python -m unittest discover -s tests -t . -v`

## 6. Challenges & Solutions
* **Polymorphic sorting** (tasks with no due date/priority) → sentinel keys + id tie-breaker.
* **Date filtering** → compare `datetime.date` objects, only for `DueDateTask`.
* **Tag filtering** → require ALL requested tags with `all()`.
* **Shared mutable default** → `tags=None` instead of `tags=[]`.

## 7. Lessons Learned
* Planning the modules first made adding tags/search/filter/sort straightforward.
* Keeping UI and logic separate allowed testing logic without simulating keyboard input.
* Writing tests early catches integration problems between modules.

## 8. Future Work
GUI, SQLite, reminders, user accounts, recurring tasks, export (CSV/PDF), edit-task feature.
