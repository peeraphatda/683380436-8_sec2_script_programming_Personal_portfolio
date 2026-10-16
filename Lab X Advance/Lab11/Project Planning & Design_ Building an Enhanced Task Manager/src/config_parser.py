import json
import os
from utils import setup_logging

logger = setup_logging(__name__)


class ConfigParser:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}

    def load_config(self):
        if not os.path.exists(self.config_path):
            logger.critical(f"Configuration file not found: {self.config_path}")
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self._validate_config()
            logger.info(f"Configuration loaded successfully from {self.config_path}")
            return self.config
        except json.JSONDecodeError as e:
            logger.critical(f"Invalid JSON format in config file: {e}")
            raise ValueError(f"Invalid JSON format in config file: {e}")

    def _validate_config(self):
        required_top_level_fields = ["global_data", "output_files", "tasks"]
        for field in required_top_level_fields:
            if field not in self.config:
                raise ValueError(f"Missing required field in config: '{field}'")
        if not isinstance(self.config["tasks"], list):
            raise ValueError("Config field 'tasks' must be a list.")

        required_by_type = {
            "generate_word_report": ["template_path", "output_path"],
            "apply_pdf_watermark": ["input_pdf", "output_pdf", "watermark_text"],
            "merge_pdfs": ["input_pdfs", "output_pdf"],
            "extract_word_text": ["input_docx", "output_text_file"],
            "extract_pdf_text": ["input_pdf", "output_text_file"],
        }
        for i, task in enumerate(self.config["tasks"]):
            if "type" not in task:
                raise ValueError(f"Task {i} is missing 'type' field.")
            if task["type"] not in required_by_type:
                raise ValueError(f"Task {i} has unknown type '{task['type']}'.")
            missing = [k for k in required_by_type[task["type"]] if k not in task]
            if missing:
                raise ValueError(f"Task {i} ({task['type']}) requires: {', '.join(missing)}.")
        logger.info("Configuration validated.")
