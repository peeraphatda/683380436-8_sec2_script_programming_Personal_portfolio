# src/utils.py
import json
import logging
import os


def setup_logging(name, level=logging.INFO, filename=None):
    """สร้าง logger สำหรับแต่ละโมดูล (ไม่เพิ่ม handler ซ้ำถ้าเรียกหลายครั้ง)"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        if filename:
            fh = logging.FileHandler(filename, encoding="utf-8")
            fh.setFormatter(formatter)
            logger.addHandler(fh)
    return logger


def save_json_report(data, filename, directory="data"):
    """บันทึก dict/list ลงไฟล์ JSON"""
    log = setup_logging(__name__)
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        log.info(f"Report saved to {filepath}")
        return True
    except IOError as e:
        log.error(f"Error saving report to JSON file: {e}")
        return False
