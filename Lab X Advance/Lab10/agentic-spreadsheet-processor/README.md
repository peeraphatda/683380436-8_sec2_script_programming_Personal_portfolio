# Lab 10: Advanced Spreadsheet Automation & Agentic Workflows

โปรเจกต์ "Agentic Sales Reporter" — โปรแกรม Python ที่อ่านไฟล์ Excel แล้วทำงานตามลำดับ **task** ที่กำหนดในไฟล์ JSON
(สูตร, conditional formatting, data validation, sheet สรุป, กราฟ) พร้อมสร้าง **Audit Log** สรุปการทำงานในไฟล์ผลลัพธ์

## โครงสร้างโปรเจกต์

```
agentic-spreadsheet-processor/
├── configs/
│   └── example_spreadsheet_config.json   # config กำหนด task ของ agent
├── data/
│   ├── input_data.xlsx                   # ข้อมูลตัวอย่าง (สร้างด้วย create_dummy_data.py)
│   └── output_report.xlsx                # ไฟล์รายงานที่ agent สร้าง
├── src/
│   ├── __init__.py
│   ├── config_parser.py                  # โหลด + ตรวจสอบ config
│   ├── spreadsheet_agent.py              # logic หลัก: dispatch task, จัดการ Excel
│   └── utils.py                          # logging และ helper
├── create_dummy_data.py                  # สร้าง input_data.xlsx
├── main.py                               # จุดเริ่มต้นโปรแกรม
├── requirements.txt
└── README.md
```

## วิธีรัน

```bash
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

python create_dummy_data.py    # 1) สร้าง data/input_data.xlsx
python main.py                 # 2) รัน agent -> data/output_report.xlsx
python main.py --config configs/example_spreadsheet_config.json   # ระบุ config เอง (ไม่บังคับ)
```

## Task ที่รองรับ

| type | ทำอะไร | field หลัก |
|---|---|---|
| `copy_data` | คัดลอกข้อมูล (พร้อม style) ไป sheet ใหม่ | `source_sheet`, `dest_sheet` |
| `calculate_column` | ใส่สูตรลงคอลัมน์ (`{row}` = เลขแถว) | `sheet`, `target_column`, `formula`, `header` |
| `conditional_format` | `color_scale` / `data_bar` / `icon_set` / `expression` | `sheet`, `range`, `rule_type` |
| `data_validation` | จำกัดค่าที่กรอก (`whole`, `decimal`, `list`, ...) | `sheet`, `range`, `validation_type` |
| `summary` | สร้าง sheet สรุปด้วยสูตร SUM/AVERAGE/MAX/MIN/INDEX-MATCH | `sheet`, `source_sheet`, `label_column`, `value_column` |
| `chart` | กราฟ `bar` / `line` / `pie` | `sheet`, `chart_type`, `data_range`, `category_range` |

เพิ่ม task ใหม่ได้โดยเขียน method `_process_xxx_task` แล้วลงทะเบียนใน `self.handlers` ของ `SpreadsheetAgent`

## ผลลัพธ์ใน output_report.xlsx

* **Raw Data** – ข้อมูลที่คัดลอก + `Total Revenue` + `Status` + conditional formatting + data validation + กราฟ Revenue by Product
* **Summary** – ยอดรวม, ค่าเฉลี่ย, สูงสุด/ต่ำสุด, สินค้าขายดีสุด (ทั้งหมดเป็นสูตร)
* **Audit Log** – บันทึกทุก task (SUCCESS / WARNING / ERROR) พร้อมเวลา

> หมายเหตุ: openpyxl เขียนสูตรเป็นข้อความโดยไม่คำนวณผล ค่าจะปรากฏเมื่อเปิดไฟล์ใน Excel
> (ถ้าอ่านด้วย `pandas` / `data_only=True` จะเห็น `None` จนกว่าไฟล์จะถูกเปิดและบันทึกใน Excel หนึ่งครั้ง)

## Debug เบื้องต้น

* `Missing required field in config` – config ขาด field ที่จำเป็นของ task นั้น ดูข้อความว่าขาด field ไหน
* `Sheet '...' not found` – ชื่อ sheet ใน config ไม่ตรงกับไฟล์ Excel (ต้องตรงตัวอักษร)
* กราฟ/สีไม่ขึ้น – ตรวจ `data_range`, `category_range`, `range` ว่าครอบคลุมข้อมูลจริง
* ดูรายละเอียดทั้งหมดที่ console และ sheet **Audit Log**

## แนวคิดต่อยอด

Google Sheets API (`gspread`), อ่านข้อมูลจาก SQLite / CSV / Web API, task dependencies, protect_sheet, CLI arguments เพิ่มเติม
