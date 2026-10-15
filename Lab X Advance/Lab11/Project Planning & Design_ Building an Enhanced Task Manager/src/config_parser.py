import json
import os


class ConfigParser:
    """อ่านและตรวจสอบความถูกต้องของ Configuration JSON"""

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self._validate_config()
            print(f"Configuration loaded successfully from {self.config_path}")
            return self.config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in config file: {e}")

    def _validate_config(self):
        required_fields = ["paths", "tasks"]
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required field in config: '{field}'")

        required_paths = ["documents_dir", "reports_dir", "templates_dir"]
        for field in required_paths:
            if field not in self.config["paths"]:
                raise ValueError(f"Missing required path in config: '{field}'")

        tasks = self.config["tasks"]
        if not isinstance(tasks, list) or not tasks:
            raise ValueError("Config must contain a non-empty 'tasks' list")

        required_task_fields = ["id", "type", "action", "params"]
        seen = set()
        for i, task in enumerate(tasks, 1):
            for field in required_task_fields:
                if field not in task:
                    raise ValueError(f"Task #{i} is missing required field: '{field}'")
            if task["id"] in seen:
                raise ValueError(f"Duplicate task id: '{task['id']}'")
            seen.add(task["id"])
