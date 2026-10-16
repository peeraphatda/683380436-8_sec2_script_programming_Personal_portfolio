# Week 11 (Advanced): Document Automation Agent

Advanced version of the Basic lab *Automating PDFs & Word Documents*.
Instead of a fixed workflow in `main.py`, a **DocumentAgent** reads a JSON config,
runs every task with `PDFTasks` (PyPDF2 + reportlab) and `WordTasks` (python-docx),
and records each step in a JSON **audit report**.

## Key Concepts Demonstrated

* **Config-driven automation** - tasks, data and file paths live in `configs/document_automation_config.json`.
* **Word templates** - `{{PLACEHOLDER}}` values are filled from `global_data` and each task's `data`; a table (with borders) is inserted at `{{TABLE_PLACEHOLDER}}`.
* **PDF watermarking** - diagonal, semi-transparent text stamped on every page.
* **PDF merging and text extraction** (PDF and Word) to `.txt` files.
* **Audit trail** - every task is logged when it starts (with its config) and when it ends (SUCCESS / ERROR), plus a run summary with the duration to `documents/reports/audit_report_<YYYYMMDD_HHMMSS>.json`.
* **Robustness** - config validation, input-file checks, per-task error handling, logging.

## Setup & How to Run

1. **Install dependencies** (virtual environment recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate.bat
   pip install -r requirements.txt
   ```
2. **Run** (from the project root)
   ```bash
   python main.py
   ```
   The required inputs are already in the repo: `templates/report_template.docx`,
   `documents/source_document.pdf`, `documents/dummy_doc1.pdf`, `documents/dummy_doc2.pdf`.

## Output (in `documents/`)

| File | Created by task |
|------|-----------------|
| `generated_report.docx` | `generate_word_report` |
| `watermarked_document.pdf` | `apply_pdf_watermark` |
| `merged_docs.pdf` | `merge_pdfs` |
| `extracted_word_text.txt` | `extract_word_text` |
| `extracted_pdf_text.txt` | `extract_pdf_text` |
| `reports/audit_report_<timestamp>.json` | the agent (one per run) |

## Screenshots (`screen-shots/`)

* `merged_docs.png` - merged_docs.pdf
* `generate_report.png` - generated_report.docx
* `watermarked_document.png` - watermarked_document.pdf

## Project Structure

```
LabADV-week-11/
├── configs/
│   └── document_automation_config.json
├── documents/
│   ├── reports/                  # audit reports (.json)
│   ├── dummy_doc1.pdf, dummy_doc2.pdf, source_document.pdf   # inputs
│   └── generated_report.docx, merged_docs.pdf, watermarked_document.pdf,
│       extracted_word_text.txt, extracted_pdf_text.txt        # outputs
├── screen-shots/
├── src/
│   ├── __init__.py
│   ├── config_parser.py          # ConfigParser: load + validate the config
│   ├── document_agent.py         # DocumentAgent: runs the tasks, writes the audit report
│   ├── pdf_tasks.py              # PDFTasks: apply_watermark, merge_pdfs, extract_text_from_pdf
│   ├── utils.py                  # logging, directories, log_audit_entry
│   └── word_tasks.py             # WordTasks: generate_report_from_template, extract_text_from_word
├── templates/
│   └── report_template.docx      # Word template with {{placeholders}}
├── .gitignore
├── README.md
├── main.py
└── requirements.txt
```

## Config format

```json
{
  "global_data": { "AUTHOR_NAME": "..." },
  "output_files": { "generated_report": "documents/generated_report.docx" },
  "tasks": [
    { "name": "...", "type": "merge_pdfs",
      "input_pdfs": ["documents/dummy_doc1.pdf", "documents/dummy_doc2.pdf"],
      "output_pdf": "documents/merged_docs.pdf" }
  ]
}
```
Task types: `generate_word_report`, `apply_pdf_watermark`, `merge_pdfs`, `extract_word_text`, `extract_pdf_text`.

## Debugging Tips

* **"Missing required input files"** - a template or input PDF listed in the config does not exist.
* **A placeholder stays as `{{...}}`** - its key is missing from `global_data` / the task's `data`.
* **Task shows `ERROR` in the audit report** - read the `details` field and the console log for the cause.
* **Empty extracted text** - the PDF is probably scanned (image only); PyPDF2 cannot OCR.
* **`ModuleNotFoundError`** - run `pip install -r requirements.txt` and start with `python main.py` from the project root.

## Extension Ideas

* Mail merge: one report per row of a CSV/Excel file
* More PDF tasks: split, rotate, encrypt/decrypt
* Scheduled runs with cron / Task Scheduler
