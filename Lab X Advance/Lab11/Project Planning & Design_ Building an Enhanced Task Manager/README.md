# Week 11 (Advanced): Document Automation Agent

Advanced version of the Basic lab *Automating PDFs & Word Documents*.
The Basic lab ran a fixed workflow from `main.py`. Here an **agent** reads a JSON
config, runs the listed PDF / Word tasks in order, and writes an **audit report**.
It reuses the Basic classes `PDFProcessor` and `WordProcessor` (same method names)
and adds new features on top of them.

## Key Concepts Demonstrated

* **Config-driven automation**: tasks are defined in `configs/document_automation_config.json`.
* **Basic features kept**: text extraction, merge, split (PDF); heading, formatted text, table, picture (Word).
* **Advanced features added**: create PDF, rotate, encrypt/decrypt, watermark, Word template filling (`{{placeholders}}`), text extraction from Word.
* **Audit trail**: every task (status, duration, detail) is recorded in `documents/reports/audit_report_<timestamp>.txt`.
* **Robustness**: validation of the config, error handling per task (`continue_on_error`), logging.

## Setup & How to Run

1. **Install dependencies** (virtual environment recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate.bat
   pip install -r requirements.txt
   ```

2. **Run** (from the project root)
   ```bash
   python main.py                                  # run all enabled tasks
   python main.py --list                           # list every task
   python main.py -t split_pdf -t encrypt_pdf      # run chosen tasks (even disabled ones)
   python main.py -c path/to/other_config.json     # use another config
   ```
   Exit code is `1` if any task failed (details are in the audit report).

## Project Structure

```
LabADV-week-11/
├── configs/
│   └── document_automation_config.json   # task definitions
├── documents/                            # generated files
│   └── reports/                          # audit reports
├── src/
│   ├── __init__.py
│   ├── config_parser.py     # ConfigParser: load + validate the JSON config
│   ├── document_agent.py    # DocumentAgent: runs tasks, writes audit report
│   ├── pdf_tasks.py         # PDFProcessor (PyPDF2 + reportlab)
│   ├── word_tasks.py        # WordProcessor (python-docx)
│   └── utils.py             # logging, directory helpers, audit report
├── templates/
│   └── report_template.docx # Word template with {{placeholders}}
├── .gitignore
├── README.md
├── requirements.txt
└── main.py                  # entry point
```

## Tasks

| type | action | level | class method |
|------|--------|-------|--------------|
| pdf  | extract_text    | Basic | `PDFProcessor.extract_text_from_pdf` |
| pdf  | merge_pdfs      | Basic | `PDFProcessor.merge_pdfs` |
| pdf  | split_pdf       | Basic | `PDFProcessor.split_pdf` |
| pdf  | create_pdf      | Adv   | `PDFProcessor.create_pdf` |
| pdf  | rotate_pages    | Adv   | `PDFProcessor.rotate_pdf` |
| pdf  | encrypt_pdf / decrypt_pdf | Adv | `PDFProcessor.encrypt_pdf` / `decrypt_pdf` |
| pdf  | add_watermark   | Adv   | `PDFProcessor.add_watermark` |
| word | create_report   | Basic | `WordProcessor.create_document / add_heading / add_paragraph / add_table / add_picture / save_document` |
| word | generate_report | Adv   | `WordProcessor.fill_template` |
| word | extract_text    | Adv   | `WordProcessor.extract_text_from_docx` |

Tasks with `"enabled": false` are skipped by default and run only with `-t <task_id>`.
Use `"{{today}}"` as a value to insert the current date.

## Debugging Tips

* **`FileNotFoundError` / task FAILED** – the task input does not exist yet; run the task that creates it first.
* **Wrong or missing password** – the PDF is encrypted; add `"password"` to the task params.
* **Empty extracted text** – the PDF may be image-based (scanned); PyPDF2 cannot OCR.
* **`ImportError: attempted relative import`** – run `python main.py` from the project root, not from inside `src/`.
* **Security** – the passwords in the config are demo values; never commit real passwords.

## Extension Ideas

* Mail merge from CSV/Excel using the Word template
* Advanced PDF parsing with `pdfminer.six` or `PyMuPDF`
* OCR for scanned PDFs
* Scheduled runs with cron / Task Scheduler
