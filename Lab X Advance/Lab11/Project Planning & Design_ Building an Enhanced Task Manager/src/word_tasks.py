# LabADV-week-11/src/word_tasks.py
# Advanced version of the Basic lab's word_processor.py:
#   Basic    : create_document, add_heading, add_paragraph, add_table,
#              add_picture, save_document   (same names/behaviour)
#   Advanced : create_template, fill_template, extract_text_from_docx
import os
import re

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

from .utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)

PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")


class WordProcessor:
    """Handles operations related to Word documents using python-docx."""

    def __init__(self):
        logger.info("WordProcessor initialized.")

    # -------------------------------------------------------------- Basic
    def create_document(self):
        """Creates a new blank Word document."""
        document = docx.Document()
        logger.info("New Word document created.")
        return document

    def add_heading(self, document, text, level=1):
        """Adds a heading to the document."""
        document.add_heading(text, level=level)
        logger.info(f"Added heading (Level {level}): '{text}'")

    def add_paragraph(self, document, text, style=None, bold=False, italic=False,
                      font_size=None, align='left'):
        """Adds a paragraph with optional formatting."""
        paragraph = document.add_paragraph(text, style=style)

        # Apply run-level formatting if specified
        if paragraph.runs:
            run = paragraph.runs[0]
            if bold:
                run.bold = True
            if italic:
                run.italic = True
            if font_size:
                run.font.size = Pt(font_size)

        # Apply paragraph alignment
        alignments = {
            'center': WD_ALIGN_PARAGRAPH.CENTER,
            'right': WD_ALIGN_PARAGRAPH.RIGHT,
            'justify': WD_ALIGN_PARAGRAPH.JUSTIFY,
        }
        paragraph.alignment = alignments.get(align, WD_ALIGN_PARAGRAPH.LEFT)

        logger.info(f"Added paragraph: '{text[:50]}...'")

    def add_table(self, document, data, include_header=True, header_bold=True, col_widths=None):
        """
        Adds a table to the document.
        `data` is a list of lists (rows). `col_widths` is a list of widths in inches.
        """
        if not data or not data[0]:
            logger.warning("Table data is empty or malformed. Skipping table creation.")
            return

        rows, cols = len(data), len(data[0])
        table = document.add_table(rows=rows, cols=cols)
        table.style = 'Table Grid'

        # Populate table
        for r_idx, row_data in enumerate(data):
            for c_idx, cell_data in enumerate(row_data):
                cell = table.cell(r_idx, c_idx)
                cell.text = str(cell_data)
                if include_header and header_bold and r_idx == 0 and cell.paragraphs[0].runs:
                    cell.paragraphs[0].runs[0].bold = True

        # Set column widths (must be set per cell for Word to respect them)
        if col_widths and len(col_widths) == cols:
            for row in table.rows:
                for c_idx, width in enumerate(col_widths):
                    row.cells[c_idx].width = Inches(width)

        logger.info(f"Added table with {rows} rows and {cols} columns.")

    def add_picture(self, document, image_path, width_inches=None):
        """Adds an image to the document with optional width scaling."""
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return False

        try:
            if width_inches:
                document.add_picture(image_path, width=Inches(width_inches))
            else:
                document.add_picture(image_path)
            logger.info(f"Added picture: {os.path.basename(image_path)}")
            return True
        except Exception as e:
            logger.error(f"Error adding picture '{image_path}': {e}")
            return False

    def save_document(self, document, output_path):
        """Saves the Word document to a specified path."""
        try:
            document.save(output_path)
            logger.info(f"Word document saved to '{output_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error saving Word document to '{output_path}': {e}")
            return False

    # ----------------------------------------------------------- Advanced
    def create_template(self, template_path):
        """Creates a default report template containing {{placeholders}}."""
        ensure_directory_exists(os.path.dirname(template_path))
        document = self.create_document()
        self.add_heading(document, "{{title}}", level=0)
        self.add_paragraph(document, "Author: {{author}}")
        self.add_paragraph(document, "Date: {{date}}")
        self.add_heading(document, "Summary", level=1)
        self.add_paragraph(document, "{{summary}}")
        self.add_heading(document, "Status", level=1)
        self.add_paragraph(document, "{{status}}")
        return self.save_document(document, template_path)

    @staticmethod
    def _replace_in_paragraph(paragraph, data):
        full = "".join(run.text for run in paragraph.runs)
        if "{{" not in full or not paragraph.runs:
            return
        new = PLACEHOLDER.sub(lambda m: str(data.get(m.group(1), m.group(0))), full)
        paragraph.runs[0].text = new          # keep formatting of the first run
        for run in paragraph.runs[1:]:
            run.text = ""

    def fill_template(self, template_path, output_path, data):
        """Fills {{placeholders}} in a .docx template and saves the result."""
        if not os.path.exists(template_path):
            logger.warning(f"Template not found, creating default: {template_path}")
            if not self.create_template(template_path):
                return False
        try:
            document = docx.Document(template_path)
            paragraphs = list(document.paragraphs)
            for table in document.tables:
                for row in table.rows:
                    for cell in row.cells:
                        paragraphs.extend(cell.paragraphs)
            for paragraph in paragraphs:
                self._replace_in_paragraph(paragraph, data)
            logger.info(f"Filled template '{template_path}'.")
            return self.save_document(document, output_path)
        except Exception as e:
            logger.error(f"Error filling template '{template_path}': {e}")
            return False

    def extract_text_from_docx(self, docx_path):
        """Extracts paragraph and table text from a .docx file. Returns None on failure."""
        if not os.path.exists(docx_path):
            logger.error(f"Word file not found: {docx_path}")
            return None
        try:
            document = docx.Document(docx_path)
            lines = [p.text for p in document.paragraphs if p.text.strip()]
            for table in document.tables:
                for row in table.rows:
                    lines.append(" | ".join(c.text.strip() for c in row.cells))
            logger.info(f"Extracted {len(lines)} line(s) from '{docx_path}'.")
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error reading Word file '{docx_path}': {e}")
            return None
