import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from config_parser import ConfigParser
from scraper_agent import ScraperAgent

def main():
    print("=== Starting Agentic Web Scraper ===")
    config_path = os.path.join(BASE_DIR, 'configs', 'example_site_config.json')
    parser = ConfigParser(config_path)
    config = parser.load_config()
    print("Config loaded successfully.")
    print("Launching browser and scraping...")
    agent = ScraperAgent(config, browser='chrome', headless=False)
    agent.run()
    print("=== Scraping Completed Finished ===")

if __name__ == "__main__":
    main()
