# LabADV-week-11/src/pdf_tasks.py
# Advanced version of the Basic lab's pdf_processor.py:
#   Basic    : extract_text_from_pdf, merge_pdfs, split_pdf   (same names/behaviour)
#   Advanced : create_pdf, rotate_pdf, encrypt_pdf, decrypt_pdf, add_watermark
import os
from io import BytesIO

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from .utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)


class PDFProcessor:
    """Handles operations related to PDF files using PyPDF2."""

    def __init__(self):
        logger.info("PDFProcessor initialized.")

    # ------------------------------------------------------------ helpers
    def _open_reader(self, pdf_path, password=None):
        """Opens a PDF, decrypting it when a password is supplied."""
        reader = PdfReader(pdf_path)
        if reader.is_encrypted:
            if not password or not reader.decrypt(password):
                raise PermissionError("PDF is encrypted: wrong or missing password")
        return reader

    def _write(self, writer, output_path):
        with open(output_path, 'wb') as f:
            writer.write(f)

    # -------------------------------------------------------------- Basic
    def extract_text_from_pdf(self, pdf_path, password=None):
        """Extracts all text from a given PDF file. Returns None on failure."""
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return None

        text_content = ""
        try:
            reader = self._open_reader(pdf_path, password)
            num_pages = len(reader.pages)
            logger.info(f"Extracting text from '{pdf_path}' ({num_pages} pages)...")

            for page in reader.pages:
                page_text = page.extract_text() or ""  # extract_text() may return empty
                text_content += page_text + "\n--- Page End ---\n"  # Separator for readability

            logger.info(f"Successfully extracted text from '{pdf_path}'.")
            return text_content
        except Exception as e:
            logger.error(f"Error extracting text from '{pdf_path}': {e}")
            return None

    def merge_pdfs(self, pdf_paths, output_path):
        """Merges multiple PDF files into a single output PDF."""
        if not pdf_paths:
            logger.warning("No PDF paths provided for merging.")
            return False

        writer = PdfWriter()
        logger.info(f"Merging PDFs into '{output_path}'...")

        for pdf_path in pdf_paths:
            if not os.path.exists(pdf_path):
                logger.warning(f"Skipping non-existent PDF for merging: {pdf_path}")
                continue
            try:
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    writer.add_page(page)
                logger.info(f"Added '{pdf_path}' to merge queue.")
            except Exception as e:
                logger.error(f"Error reading PDF '{pdf_path}' for merging: {e}")
                continue

        if len(writer.pages) == 0:
            logger.warning("No pages were added to the merged PDF. Output file not created.")
            return False

        try:
            self._write(writer, output_path)
            logger.info(f"PDFs successfully merged to '{output_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error writing merged PDF to '{output_path}': {e}")
            return False

    def split_pdf(self, pdf_path, output_dir=".", pages_per_split=1):
        """Splits a PDF into smaller PDFs, each containing `pages_per_split` pages."""
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return False
        if pages_per_split < 1:
            logger.error("pages_per_split must be >= 1")
            return False

        ensure_directory_exists(output_dir)
        try:
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            logger.info(f"Splitting '{pdf_path}' ({total_pages} pages) into chunks of {pages_per_split} page(s).")

            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            for i in range(0, total_pages, pages_per_split):
                writer = PdfWriter()
                part_no = (i // pages_per_split) + 1
                output_filename = os.path.join(output_dir, f"{base_name}_part_{part_no}.pdf")

                for j in range(i, min(i + pages_per_split, total_pages)):
                    writer.add_page(reader.pages[j])

                self._write(writer, output_filename)
                logger.info(f"Created split PDF: {output_filename}")

            logger.info(f"Successfully split '{pdf_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error splitting PDF '{pdf_path}': {e}")
            return False

    # ----------------------------------------------------------- Advanced
    def create_pdf(self, output_path, title="Untitled", paragraphs=None):
        """Creates a simple PDF with a title and paragraphs (reportlab)."""
        try:
            styles = getSampleStyleSheet()
            story = [Paragraph(title, styles["Title"]), Spacer(1, 0.5 * cm)]
            for text in paragraphs or []:
                story.append(Paragraph(text, styles["BodyText"]))
                story.append(Spacer(1, 0.3 * cm))
            SimpleDocTemplate(output_path, pagesize=A4, title=title).build(story)
            logger.info(f"Created PDF: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating PDF '{output_path}': {e}")
            return False

    def rotate_pdf(self, pdf_path, output_path, angle=90, pages=None):
        """Rotates all (or the selected 1-based) pages by a multiple of 90 degrees."""
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return False
        if angle % 90 != 0:
            logger.error("Rotation angle must be a multiple of 90.")
            return False
        try:
            reader = self._open_reader(pdf_path)
            writer = PdfWriter()
            for number, page in enumerate(reader.pages, 1):
                if not pages or number in pages:
                    page.rotate(angle)
                writer.add_page(page)
            self._write(writer, output_path)
            logger.info(f"Rotated '{pdf_path}' by {angle} degrees -> '{output_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error rotating PDF '{pdf_path}': {e}")
            return False

    def encrypt_pdf(self, pdf_path, output_path, password):
        """Password-protects a PDF."""
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return False
        if not password:
            logger.error("A password is required to encrypt a PDF.")
            return False
        try:
            reader = self._open_reader(pdf_path)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.encrypt(password)
            self._write(writer, output_path)
            logger.info(f"Encrypted '{pdf_path}' -> '{output_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error encrypting PDF '{pdf_path}': {e}")
            return False

    def decrypt_pdf(self, pdf_path, output_path, password):
        """Removes password protection from a PDF."""
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return False
        try:
            reader = self._open_reader(pdf_path, password)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            self._write(writer, output_path)
            logger.info(f"Decrypted '{pdf_path}' -> '{output_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error decrypting PDF '{pdf_path}': {e}")
            return False

    def add_watermark(self, pdf_path, output_path, text="WATERMARK",
                      opacity=0.2, font_size=60, angle=45):
        """Stamps diagonal text over every page of a PDF."""
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return False
        try:
            reader = self._open_reader(pdf_path)
            writer = PdfWriter()
            for page in reader.pages:
                width = float(page.mediabox.width)
                height = float(page.mediabox.height)
                buffer = BytesIO()
                c = canvas.Canvas(buffer, pagesize=(width, height))
                c.saveState()
                c.setFillGray(0.5, opacity)
                c.setFont("Helvetica-Bold", font_size)
                c.translate(width / 2, height / 2)
                c.rotate(angle)
                c.drawCentredString(0, 0, text)
                c.restoreState()
                c.save()
                buffer.seek(0)
                page.merge_page(PdfReader(buffer).pages[0])
                writer.add_page(page)
            self._write(writer, output_path)
            logger.info(f"Watermarked '{pdf_path}' with '{text}' -> '{output_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error watermarking PDF '{pdf_path}': {e}")
            return False
