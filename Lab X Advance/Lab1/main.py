import sys
import os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from config_parser import ConfigParser
from scraper_agent import ScraperAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    config_path = os.path.join(os.path.dirname(__file__), 'configs', 'example_site_config.json')
    try:
        parser = ConfigParser(config_path)
        config = parser.load_config()

        # หากต้องการดูการทำงานของเบราว์เซอร์ขณะรัน ให้เปลี่ยน headless=False
        agent = ScraperAgent(config, browser='chrome', headless=True)
        agent.run()
    except Exception as e:
        logging.critical(f"Execution failed: {e}")

if __name__ == "__main__":
    main()