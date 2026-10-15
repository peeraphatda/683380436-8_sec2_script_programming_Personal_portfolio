# agentic-data-processor/main.py
import sys
import os

# เรียกใช้โมดูลผ่านแพ็กเกจ src. โดยตรง
from src.config_parser import ConfigParser
from src.data_agent import DataAgent
from src.utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)

def check_required_input_files(config):
    """
    Checks if all input files specified in the config exist before starting the agent.
    This check needs to be robust for all task types.
    """
    required_files_exist = True
    for task in config['tasks']:
        if task['type'] in ['load_csv', 'load_json']:
            file_path = task['file_path']
            if not os.path.exists(file_path):
                logger.critical(f"Required input file '{file_path}' not found for task '{task['name']}'.")
                required_files_exist = False
    return required_files_exist

def main():
    """
    Main entry point for the Agentic Data Processor.
    Loads config and runs the agent.
    """
    base_dir = os.path.dirname(__file__)
    config_file_path = os.path.join(base_dir, 'configs', 'data_pipeline_config.json')
    
    try:
        # Ensure data and configs directories exist
        ensure_directory_exists(os.path.join(base_dir, 'data'))
        ensure_directory_exists(os.path.join(base_dir, 'configs'))
        ensure_directory_exists(os.path.join(base_dir, 'reports')) # For audit reports

        logger.info(f"Loading configuration from: {config_file_path}")
        config_parser = ConfigParser(config_file_path)
        config = config_parser.load_config()

        # Update file paths in config to be absolute for the handlers
        # This makes paths in config relative to the project root for readability
        for task in config['tasks']:
            if 'file_path' in task:
                task['file_path'] = os.path.join(base_dir, task['file_path'])

            if 'output_data_key' in task:
                # Special handling for outputs to ensure their directories exist
                # This assumes output_data_key sometimes refers to a final file path for saving
                if task['type'] in ['save_csv', 'save_json'] and 'file_path' in task:
                    ensure_directory_exists(os.path.dirname(task['file_path']))

        # Check if all required input files exist before starting the agent run
        if not check_required_input_files(config):
            logger.critical("One or more required input files are missing. Please create them as per README.md and config.")
            return

        logger.info("Initializing Data Agent...")
        agent = DataAgent(config)
        
        logger.info("Running Data Agent workflow...")
        agent.run()

        logger.info("Data automation process completed.")

    except FileNotFoundError as e:
        logger.critical(f"File system error: {e}")
        logger.info("Please ensure all specified input files and configurations exist.")
    except ValueError as e:
        logger.critical(f"Configuration error: {e}")
        logger.info("Please check the format and required fields in your config file.")
    except ImportError as e:
        logger.critical(f"Missing required library: {e}. All required libraries for this scaffold are built-in Python modules.")
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred during execution: {e}", exc_info=True)

if __name__ == "__main__":
    main()