# LabADV-week-11/src/document_agent.py
import os
import time

from .pdf_tasks import PDFProcessor
from .word_tasks import WordProcessor
from .utils import ensure_directory_exists, setup_logging, today, write_audit_report

logger = setup_logging(__name__)


class DocumentAgent:
    """Reads the task list from the config, runs each task with the Basic
    processors (PDFProcessor / WordProcessor) and records an audit report."""

    def __init__(self, config, base_dir='.'):
        self.config = config
        paths = config["paths"]
        self.documents_dir = os.path.join(base_dir, paths["documents_dir"])
        self.reports_dir = os.path.join(base_dir, paths["reports_dir"])
        self.templates_dir = os.path.join(base_dir, paths["templates_dir"])
        for directory in (self.documents_dir, self.reports_dir, self.templates_dir):
            ensure_directory_exists(directory)

        self.continue_on_error = config.get("settings", {}).get("continue_on_error", True)
        self.pdf_proc = PDFProcessor()
        self.word_proc = WordProcessor()
        self.results = []

        # (type, action) -> handler
        self.registry = {
            ("pdf", "create_pdf"): self._create_pdf,
            ("pdf", "extract_text"): self._extract_pdf_text,
            ("pdf", "merge_pdfs"): self._merge_pdfs,
            ("pdf", "split_pdf"): self._split_pdf,
            ("pdf", "rotate_pages"): self._rotate_pdf,
            ("pdf", "encrypt_pdf"): self._encrypt_pdf,
            ("pdf", "decrypt_pdf"): self._decrypt_pdf,
            ("pdf", "add_watermark"): self._add_watermark,
            ("word", "create_report"): self._create_report,
            ("word", "generate_report"): self._generate_report,
            ("word", "extract_text"): self._extract_word_text,
        }

    # ------------------------------------------------------------ helpers
    def _doc(self, name):
        return os.path.join(self.documents_dir, name)

    @staticmethod
    def _require(ok, message):
        if not ok:
            raise RuntimeError(message)

    @staticmethod
    def _resolve(value):
        return today() if value == "{{today}}" else value

    def _write_text(self, name, text):
        with open(self._doc(name), 'w', encoding='utf-8') as f:
            f.write(text)

    # -------------------------------------------------------- PDF handlers
    def _create_pdf(self, p):
        ok = self.pdf_proc.create_pdf(self._doc(p["output"]), p.get("title", "Untitled"),
                                      p.get("paragraphs"))
        self._require(ok, f"Could not create {p['output']}")
        return f"Created {p['output']}"

    def _extract_pdf_text(self, p):
        text = self.pdf_proc.extract_text_from_pdf(self._doc(p["input"]), p.get("password"))
        self._require(text is not None, f"Could not extract text from {p['input']}")
        self._write_text(p["output"], text)
        return f"Extracted {text.count('--- Page End ---')} page(s) to {p['output']}"

    def _merge_pdfs(self, p):
        ok = self.pdf_proc.merge_pdfs([self._doc(n) for n in p["inputs"]], self._doc(p["output"]))
        self._require(ok, f"Could not merge into {p['output']}")
        return f"Merged {len(p['inputs'])} file(s) into {p['output']}"

    def _split_pdf(self, p):
        out_dir = self._doc(p.get("output_dir", "split"))
        ok = self.pdf_proc.split_pdf(self._doc(p["input"]), out_dir, p.get("pages_per_split", 1))
        self._require(ok, f"Could not split {p['input']}")
        return f"Split {p['input']} into {out_dir}"

    def _rotate_pdf(self, p):
        ok = self.pdf_proc.rotate_pdf(self._doc(p["input"]), self._doc(p["output"]),
                                      p.get("angle", 90), p.get("pages"))
        self._require(ok, f"Could not rotate {p['input']}")
        return f"Rotated {p['input']} by {p.get('angle', 90)} degrees -> {p['output']}"

    def _encrypt_pdf(self, p):
        ok = self.pdf_proc.encrypt_pdf(self._doc(p["input"]), self._doc(p["output"]), p.get("password"))
        self._require(ok, f"Could not encrypt {p['input']}")
        return f"Encrypted {p['input']} -> {p['output']}"

    def _decrypt_pdf(self, p):
        ok = self.pdf_proc.decrypt_pdf(self._doc(p["input"]), self._doc(p["output"]), p.get("password"))
        self._require(ok, f"Could not decrypt {p['input']} (wrong password?)")
        return f"Decrypted {p['input']} -> {p['output']}"

    def _add_watermark(self, p):
        ok = self.pdf_proc.add_watermark(self._doc(p["input"]), self._doc(p["output"]),
                                         p.get("text", "WATERMARK"), p.get("opacity", 0.2),
                                         p.get("font_size", 60), p.get("angle", 45))
        self._require(ok, f"Could not watermark {p['input']}")
        return f"Watermarked '{p.get('text', 'WATERMARK')}' -> {p['output']}"

    # ------------------------------------------------------ Word handlers
    def _create_report(self, p):
        """Basic 'PDF to Word reporter' workflow (Task 1 of the Basic main.py)."""
        extracted = None
        if p.get("pdf_input"):
            extracted = self.pdf_proc.extract_text_from_pdf(self._doc(p["pdf_input"]))
            self._require(extracted is not None, f"Could not extract text from {p['pdf_input']}")

        wp = self.word_proc
        doc = wp.create_document()
        wp.add_heading(doc, p["title"], level=1)
        wp.add_paragraph(doc, p.get("intro", "Automatically generated report."),
                         bold=True, font_size=12)
        if extracted:
            wp.add_paragraph(doc, "--- Extracted Content from PDF ---", italic=True,
                             font_size=10, align='center')
            wp.add_paragraph(doc, extracted)
        if p.get("table"):
            wp.add_heading(doc, "Summary Data", level=2)
            table = [[self._resolve(cell) for cell in row] for row in p["table"]]
            wp.add_table(doc, table, col_widths=p.get("col_widths"))
        if p.get("image"):
            wp.add_picture(doc, self._doc(p["image"]), p.get("image_width", 4.0))

        self._require(wp.save_document(doc, self._doc(p["output"])), f"Could not save {p['output']}")
        return f"Created {p['output']}"

    def _generate_report(self, p):
        data = {k: self._resolve(v) for k, v in p.get("data", {}).items()}
        ok = self.word_proc.fill_template(os.path.join(self.templates_dir, p["template"]),
                                          self._doc(p["output"]), data)
        self._require(ok, f"Could not generate {p['output']} from {p['template']}")
        return f"Generated {p['output']} from template {p['template']}"

    def _extract_word_text(self, p):
        text = self.word_proc.extract_text_from_docx(self._doc(p["input"]))
        self._require(text is not None, f"Could not read {p['input']}")
        self._write_text(p["output"], text)
        return f"Extracted {len(text.splitlines())} line(s) to {p['output']}"

    # --------------------------------------------------------------- runner
    def _record(self, task, status, detail, start):
        self.results.append({
            "id": task["id"], "type": task["type"], "action": task["action"],
            "description": task.get("description", ""), "status": status,
            "detail": detail, "duration": time.perf_counter() - start,
        })

    def run(self, only=None):
        """Runs enabled tasks (or only the selected ids) and writes the audit report."""
        logger.info(f"Starting: {self.config.get('project', {}).get('name', 'Document Agent')}")
        for task in self.config["tasks"]:
            if only:
                if task["id"] not in only:
                    continue
            elif not task.get("enabled", True):
                logger.info(f"SKIP {task['id']} (disabled; run with -t {task['id']})")
                continue

            start = time.perf_counter()
            try:
                handler = self.registry.get((task["type"], task["action"]))
                if handler is None:
                    raise ValueError(f"Unknown task: {task['type']}.{task['action']}")
                detail = handler(task["params"])
                logger.info(f"OK   {task['id']}: {detail}")
                self._record(task, "success", detail, start)
            except Exception as e:
                detail = f"{type(e).__name__}: {e}"
                logger.error(f"FAIL {task['id']}: {detail}")
                self._record(task, "failed", detail, start)
                if not self.continue_on_error:
                    break

        report = write_audit_report(self.reports_dir, self.results, self.config.get("project", {}))
        logger.info(f"Audit report saved: {report}")
        return report
