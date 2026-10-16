import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config_parser import ConfigParser
from document_agent import DocumentAgent
from utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)


def check_required_files(config):
    """ตรวจสอบไฟล์ที่ต้องมีอยู่ก่อนรัน (template และ PDF ต้นฉบับ)"""
    ok = True
    for task in config['tasks']:
        required = []
        if 'template_path' in task:
            required.append(task['template_path'])
        if task['type'] != 'extract_word_text' and 'input_pdf' in task:
            required.append(task['input_pdf'])
        required += task.get('input_pdfs', [])
        for path in required:
            if not os.path.exists(path):
                logger.error(f"Required input file not found: {path}")
                ok = False
    return ok


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(base_dir, 'configs', 'document_automation_config.json')

    ensure_directory_exists(os.path.join(base_dir, 'documents'))
    ensure_directory_exists(os.path.join(base_dir, 'templates'))

    config_parser = ConfigParser(config_file_path)
    config = config_parser.load_config()

    # แปลง path ใน config ให้เป็น Absolute path
    for key, value in config['output_files'].items():
        config['output_files'][key] = os.path.join(base_dir, value)
    for task in config['tasks']:
        for k in ['template_path', 'output_path', 'input_pdf', 'output_pdf', 'input_docx', 'output_text_file']:
            if k in task:
                task[k] = os.path.join(base_dir, task[k])
        if 'input_pdfs' in task:
            task['input_pdfs'] = [os.path.join(base_dir, p) for p in task['input_pdfs']]

    if not check_required_files(config):
        logger.critical("Missing required input files! Please check the template and the input PDFs in 'documents/'.")
        return

    agent = DocumentAgent(config)
    agent.run()
    logger.info("Document automation process completed.")


if __name__ == "__main__":
    main()
