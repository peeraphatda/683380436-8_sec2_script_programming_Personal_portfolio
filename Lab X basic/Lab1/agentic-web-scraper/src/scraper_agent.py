import time
from selenium.webdriver.common.by import By
from driver_manager import DriverManager
from data_models import Product
from utils import save_data_to_json, wait_for_element

class ScraperAgent:
    def __init__(self, config, browser='chrome', headless=True):
        self.config = config
        self.driver_manager = DriverManager(browser_name=browser, headless=headless)
        self.driver = None
        self.scraped_products = []
        self.max_pages = config.get("max_pages", 3)

    def scrape_page(self):
        items = self.driver.find_elements(By.CSS_SELECTOR, self.config["item_container_selector"])
        for item in items:
            try:
                name = item.find_element(By.CSS_SELECTOR, self.config["item_data_selectors"]["name"]).text
                price = item.find_element(By.CSS_SELECTOR, self.config["item_data_selectors"]["price"]).text
                if name and price:
                    self.scraped_products.append(Product(name=name, price=price).to_dict())
            except Exception:
                continue

    def run(self):
        self.driver = self.driver_manager.get_driver()
        if not self.driver:
            return
        try:
            self.driver.get(self.config["start_url"])
            current_page = 1
            while current_page <= self.max_pages:
                self.scrape_page()
                time.sleep(self.config.get("delay_between_pages", 2))
                next_btn = wait_for_element(self.driver, By.CSS_SELECTOR, self.config["pagination_selector"])
                if next_btn and next_btn.is_displayed():
                    next_btn.click()
                    current_page += 1
                else:
                    break
        finally:
            self.driver_manager.quit_driver()
            save_data_to_json(self.scraped_products, "scraped_products.json")
