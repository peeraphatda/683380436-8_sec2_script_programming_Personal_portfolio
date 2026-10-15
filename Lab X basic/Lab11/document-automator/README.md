# Week 10: Automating PDFs & Word Documents

This project demonstrates how to automate common tasks involving PDF and Word documents
using Python. It uses `PyPDF2` for PDF manipulation and `python-docx` for Word document
creation.

## Key Concepts Demonstrated

* **PDF Text Extraction**: Reading text content from PDF files.
* **PDF Merging & Splitting**: Combining or splitting PDF files.
* **Word Document Creation**: Generating new `.docx` files programmatically.
* **Adding Content to Word**: Headings, paragraphs, formatted text (bold, italic, size), tables, pictures.
* **Modular Design**: PDF and Word logic live in separate modules.
* **Robustness**: Error handling and logging throughout.

## Setup & How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/document-automator.git
   cd document-automator
   ```

2. **Install dependencies** (virtual environment recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate.bat
   pip install PyPDF2 python-docx
   ```

3. **Input documents** (already included in `documents/`)
   * `input_article.pdf` – text is extracted and inserted into the Word report
   * `dummy_doc1.pdf`, `dummy_doc2.pdf` – merged into `merged_output.pdf`

4. **Run** (from the project root)
   ```bash
   python main.py
   ```
   Output:
   * `documents/output_report.docx` – heading, formatted text, extracted PDF text, summary table
   * `documents/merged_output.pdf` – the two dummy PDFs merged

## Project Structure

```
document-automator/
├── documents/
│   ├── dummy_doc1.pdf
│   ├── dummy_doc2.pdf
│   └── input_article.pdf
├── src/
│   ├── __init__.py
│   ├── pdf_processor.py     # PyPDF2: extract, merge, split
│   ├── utils.py             # logging, directory helpers
│   └── word_processor.py    # python-docx: create, add content, save
├── .gitignore
├── README.md
└── main.py                  # entry point
```

## Debugging Tips

* **`FileNotFoundError`** – make sure the input PDFs are in `documents/` with exact names.
* **`PdfReadError`** – the PDF may be corrupted or encrypted.
* **Empty Word document** – the PDF may be image-based (scanned) with no selectable text; use OCR.
* **`ImportError: attempted relative import`** – run `python main.py` from the project root, not from inside `src/`.

## Extension Ideas

* Template-based generation (replace `{{placeholders}}` in a `.docx`)
* Mail merge from CSV/Excel
* Advanced PDF parsing with `pdfminer.six` or `PyMuPDF`
* PDF encryption / rotation with PyPDF2
