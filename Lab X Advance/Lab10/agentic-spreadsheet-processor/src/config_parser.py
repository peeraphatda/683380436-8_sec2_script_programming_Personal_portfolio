# src/config_parser.py
import json
import os

from .utils import setup_logging

logger = setup_logging(__name__)

# field ที่จำเป็นของแต่ละ task type (นอกเหนือจาก "type")
REQUIRED_FIELDS = {
    "copy_data": ["source_sheet", "dest_sheet"],
    "calculate_column": ["sheet", "target_column", "formula"],
    "conditional_format": ["sheet", "range", "rule_type"],
    "chart": ["sheet", "chart_type", "data_range"],
    "summary": ["sheet", "source_sheet", "value_column", "label_column"],
    "data_validation": ["sheet", "range", "validation_type"],
}


class ConfigParser:
    """โหลดและตรวจสอบ (validate) ไฟล์ config แบบ JSON"""

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}

    def load_config(self):
        if not os.path.exists(self.config_path):
            logger.critical(f"Configuration file not found: {self.config_path}")
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            logger.critical(f"Invalid JSON format in config file: {e}")
            raise ValueError(f"Invalid JSON format in config file: {e}")

        self._validate_config()
        logger.info(f"Configuration loaded successfully from {self.config_path}")
        return self.config

    def _validate_config(self):
        for field in ("input_file", "output_file", "tasks"):
            if field not in self.config:
                raise ValueError(f"Missing required field in config: '{field}'")

        if not isinstance(self.config["tasks"], list):
            raise ValueError("Config field 'tasks' must be a list.")

        for i, task in enumerate(self.config["tasks"], start=1):
            task_type = task.get("type")
            if not task_type:
                raise ValueError(f"Task {i} is missing 'type' field.")
            # task ที่รู้จักจะถูกตรวจ field ที่จำเป็น; ที่ไม่รู้จักจะถูก agent เตือนตอนรัน
            for field in REQUIRED_FIELDS.get(task_type, []):
                if field not in task:
                    raise ValueError(f"Task {i} ('{task_type}') requires field '{field}'.")

        logger.info("Configuration validated.")
