# Submission Checklist – Week 12 Final Project

## Code & Structure
- [x] `src/` package with `__init__.py`, `task.py`, `data_persistence.py`, `task_manager.py`, `cli_interface.py`
- [x] `data/tasks.json` with sample tasks for demo
- [x] `tests/` with `__init__.py` and `test_task_manager.py`
- [x] `main.py` entry point runs with `python main.py`
- [x] `.gitignore`, `README.md`, `PLAN.md`

## Features
- [x] Tags (`add_tag`, `remove_tag`, in `to_dict`, `__str__`, CLI input)
- [x] Search (case-insensitive, partial, description + tags)
- [x] Filter (status, due-date range, priority, tags, combined)
- [x] Sort (id, description, completed, due_date, priority; missing values handled)
- [x] Data persistence for all task types incl. tags
- [x] Error handling (invalid date / priority / ID / corrupted JSON)

## Quality
- [x] All unit tests pass (32 tests)
- [x] Docstrings on modules, classes, key methods
- [x] PEP 8 style, `logging` instead of debug prints
- [x] README / PLAN updated with features, known issues, future work

## Before Submitting (do yourself)
- [ ] Replace `YOUR_USERNAME` in README with your GitHub username
- [ ] Add your name / student ID to README and presentation
- [ ] Run `python main.py` once end-to-end
- [ ] Run tests one last time
- [ ] Commit & push; check the repo on GitHub matches the structure
- [ ] Practice the presentation (intro, problem, demo, architecture, challenges, lessons, future work, Q&A)
- [ ] Have a backup plan for the demo (screenshots / recorded video)
