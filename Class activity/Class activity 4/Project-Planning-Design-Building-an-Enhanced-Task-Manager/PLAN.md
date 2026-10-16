# Project Plan: Enhanced Task Manager CLI

## 1. Introduction
เอกสารนี้อธิบายแผนการพัฒนา Task Manager แบบ CLI เวอร์ชันปรับปรุง
เน้น **modularity**, ฟีเจอร์การจัดการงานขั้นสูง (tags / search / filter / sort)
และ **separation of concerns** เพื่อให้พัฒนาต่อและดูแลรักษาได้ง่าย

**สถานะ:** ✅ ออกแบบเสร็จ และ implement ครบทุกฟีเจอร์ที่วางแผนไว้ในรอบนี้

## 2. Requirements

### 2.1 Functional Requirements
* **Core CRUD**
  * สร้างงานพร้อม description, สถานะ (เริ่มต้น Pending) และ tags (ไม่บังคับ)
  * งานพิเศษ: `DueDateTask` (วันที่ `YYYY-MM-DD`), `PriorityTask` (High / Medium / Low)
  * แสดงรายการงานพร้อมรายละเอียดเฉพาะประเภทและ tags
  * เปลี่ยนสถานะเป็นเสร็จ / ลบงานตาม ID
* **Advanced Retrieval**
  * **Search:** ค้นด้วย keyword ใน description หรือ tags
  * **Filter:** สถานะ, ช่วงวันครบกำหนด (ก่อน/หลัง), priority, tag — ใช้หลายเงื่อนไขพร้อมกัน (AND)
  * **Sort:** id (ค่าเริ่มต้น), due_date, priority, status, description — เรียงย้อนกลับได้
* **Persistence**
  * บันทึกลง `data/tasks.json` ทุกครั้งที่เพิ่ม/เสร็จ/ลบ
  * โหลดตอนเริ่มโปรแกรม พร้อมสร้าง subclass ให้ถูกต้องจากฟิลด์ `_type`

### 2.2 Non-Functional Requirements
* **Usability:** เมนูและข้อความแจ้งชัดเจน
* **Reliability:** จัดการ input ผิดพลาด (วันที่ผิดรูปแบบ, ID ไม่ใช่ตัวเลข, priority ไม่ถูกต้อง, ไฟล์ JSON เสีย)
* **Maintainability:** โค้ดแยกโมดูล มี docstring และ unit tests
* **Extensibility:** เพิ่ม task type / เงื่อนไข filter / เปลี่ยน persistence ได้โดยไม่รื้อระบบ
* **Performance:** รองรับงานหลักร้อยรายการได้ทันที

## 3. High-Level Architecture

```
main.py  ──►  CLIInterface  ──►  TaskManager  ──►  DataPersistence  ──►  data/tasks.json
 (orchestrator)   (UI layer)      (business logic)      (data layer)
                                        │
                                        └──► Task / DueDateTask / PriorityTask (models)
```

### 3.1 Module Responsibilities
* **`task.py` (Models):** นิยาม `Task` และ subclass; จัดการ tags (`add_tag`, `remove_tag`);
  `to_dict()` สำหรับ serialize; `__str__` / `__repr__`
* **`data_persistence.py` (Data Layer):** อ่าน/เขียน JSON ทั้งหมด, แปลง dict ↔ Task object, จัดการ error ของไฟล์
* **`task_manager.py` (Business Logic):** จัดการชุดของ Task; `add_*`, `complete_task`, `delete_task`,
  `get_all_tasks`, `search_tasks`, `filter_tasks`, `sort_tasks`; ดูแล `next_id`; **ไม่มี print/input และไม่แตะไฟล์โดยตรง**
* **`cli_interface.py` (UI Layer):** แสดงเมนู, รับ/ตรวจสอบ input, แสดงผล; เรียก `TaskManager` เท่านั้น **ไม่มีตรรกะธุรกิจ**
* **`main.py` (Orchestrator):** สร้าง `TaskManager` และ `CLIInterface` แล้วเริ่ม loop

### 3.2 Data Model
* `Task` มี attribute ใหม่ `tags` (list ของ string)
* JSON: ทุก task มี key `tags` เช่น `"tags": ["work", "python"]` และ `_type` ระบุประเภท

### 3.3 Design Decisions (Search / Filter / Sort)
| หัวข้อ | การตัดสินใจ |
|---|---|
| Search | substring แบบ case-insensitive ทั้ง description และ tags |
| Filter | เงื่อนไขที่ไม่ใส่ = ไม่กรอง; due date กรองเฉพาะ `DueDateTask`, priority กรองเฉพาะ `PriorityTask` |
| Sort by due_date / priority | งานที่ไม่มีค่านั้นอยู่ **ท้ายสุดเสมอ** แม้เรียงย้อนกลับ |
| Priority order | High → Medium → Low (กำหนดใน `PRIORITY_ORDER`) |
| Creation date | ใช้ ID แทน (ID เพิ่มขึ้นตามลำดับการสร้าง) |

## 4. Implementation Plan & Status
1. ✅ Refactor `Task`, `DueDateTask`, `PriorityTask` ไว้ใน `src/task.py`
2. ✅ `data_persistence.py` แยก JSON load/save ออกจาก `TaskManager`
3. ✅ `cli_interface.py` รวม `print`/`input` ทั้งหมด; `main.py` เป็น orchestrator
4. ✅ Tags: ใส่ตอนสร้างงานและแสดงผลในทุกประเภท
5. ✅ Search (เมนู 7)
6. ✅ Filter (เมนู 8)
7. ✅ Sort (เมนู 9)
8. ✅ Unit tests (`tests/test_task_manager.py`)

## 5. Challenges & Considerations
* **Date range filtering:** ตอนนี้ใช้ "ก่อน/ตั้งแต่วันที่"; อนาคตอาจรองรับ "สัปดาห์หน้า"
* **Sorting across types:** แก้โดยวางงานที่ไม่มีค่าไว้ท้าย
* **CLI complexity:** รักษาเมนูให้เข้าใจง่ายเมื่อฟีเจอร์เพิ่มขึ้น
* **Error handling:** ตรวจสอบ input ที่ชั้น UI และ file error ที่ชั้น persistence

## 6. Future Enhancements
* Reminders สำหรับงานใกล้ครบกำหนด (แสดงตอนเริ่มโปรแกรม)
* Edit task / จัดการ tag หลังสร้างงาน
* User accounts (หลายผู้ใช้)
* GUI (Tkinter / PyQt)
* SQLite แทน JSON
* Export / Import CSV
* Undo / Redo
