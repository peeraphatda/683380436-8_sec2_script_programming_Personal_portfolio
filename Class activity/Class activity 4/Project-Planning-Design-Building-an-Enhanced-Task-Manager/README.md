# Enhanced Task Manager CLI (Week 11)

โปรเจกต์ Task Manager แบบ Command-Line ที่ออกแบบด้วยหลัก **Project Planning & Design**
แยกโค้ดเป็นโมดูลชัดเจน (Separation of Concerns) และรองรับการขยายในอนาคต

## Features (Implemented ✅)

| ฟีเจอร์ | รายละเอียด |
|---|---|
| **Basic CRUD** | เพิ่ม / แสดง / เปลี่ยนสถานะเป็นเสร็จ / ลบงาน |
| **Task Types** | `Task` (ทั่วไป), `DueDateTask` (มีวันครบกำหนด), `PriorityTask` (มีระดับความสำคัญ) |
| **Tags** | ใส่ได้หลาย tag ต่องาน (เช่น `work,urgent`) |
| **Search** | ค้นหาจากคำใน description หรือ tags (ไม่สนตัวพิมพ์เล็ก/ใหญ่) |
| **Filter** | กรองตามสถานะ, ช่วงวันครบกำหนด, priority, tag (รวมหลายเงื่อนไขพร้อมกันได้) |
| **Sort** | เรียงตาม id, due_date, priority, status, description (เรียงย้อนกลับได้) |
| **Persistence** | บันทึก/โหลดอัตโนมัติที่ `data/tasks.json` |

## How to Run

```bash
cd enhanced-task-manager-design
python main.py
```

ต้องใช้ Python 3.8+ (ไม่ต้องติดตั้งไลบรารีเพิ่ม)

> ถ้าภาษาไทยใน Terminal (Windows) แสดงผลเพี้ยน ให้พิมพ์ `chcp 65001` ก่อนรัน

## How to Test

```bash
python -m unittest discover -s tests -v
```

## Project Structure

```
enhanced-task-manager-design/
├── src/
│   ├── __init__.py          # ทำให้ 'src' เป็น Python package
│   ├── task.py              # Models: Task, DueDateTask, PriorityTask
│   ├── data_persistence.py  # Data layer: โหลด/บันทึก JSON
│   ├── task_manager.py      # Business logic: add/complete/delete/search/filter/sort
│   └── cli_interface.py     # UI layer: เมนูและ input/output ทั้งหมด
├── tests/
│   └── test_task_manager.py # Unit tests
├── data/
│   └── tasks.json           # ข้อมูลงาน (สร้าง/อัปเดตอัตโนมัติ)
├── main.py                  # Entry point / Orchestrator
├── .gitignore
├── README.md
└── PLAN.md                  # เอกสารวางแผนและออกแบบ
```

## Design Principles

* **Modularity** – แบ่งระบบเป็นโมดูลย่อยที่เปลี่ยนแทนกันได้
* **Separation of Concerns** – UI / Business Logic / Data แยกจากกันเด็ดขาด
  (`TaskManager` ไม่มี `print`/`input`, `CLIInterface` ไม่มีตรรกะธุรกิจ)
* **Polymorphism** – แต่ละ Task class มี `to_dict()` และ `__str__()` ของตัวเอง
* **Extensibility** – เพิ่ม task type ใหม่หรือเปลี่ยน JSON เป็น SQLite ได้โดยไม่ต้องรื้อโค้ดส่วนอื่น

## Example Usage

```
เลือกเมนู (0-9): 7
กรอกคำค้นหา (ค้นใน description และ tags): python

--- ผลการค้นหา 'python' (2 รายการ) ---
- ID: 3 | Description: Implement ... | Status: Pending | Priority: High | Tags: coding, python, priority
- ID: 4 | Description: ทบทวน ... | Status: Pending | Priority: Medium | Tags: review, python
```

## Future Ideas

* Reminders สำหรับงานใกล้ครบกำหนด
* แก้ไขงาน (Edit) และจัดการ tag (เพิ่ม/ลบหลังสร้างงาน)
* Priority แบบตัวเลข 1–5
* เปลี่ยน persistence เป็น SQLite
* GUI (Tkinter / PyQt)
