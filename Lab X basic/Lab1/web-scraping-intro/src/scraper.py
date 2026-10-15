import requests
from bs4 import BeautifulSoup

class SimpleWebScraper:
    """
    A class to encapsulate basic web scraping functionality.
    """
    def __init__(self, target_url):
        self.target_url = target_url

    def _get_html_content(self):
        """
        Downloads the HTML content from the target URL.
        """
        print(f"Downloading content from: {self.target_url}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(self.target_url, headers=headers, timeout=10)
            response.raise_for_status()
            print("Successfully downloaded content.")
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error downloading page: {e}")
            return None

    def scrape_main_titles(self):
        """
        Scrapes the main book title and chapter titles from the homepage.
        """
        html_content = self._get_html_content()
        if not html_content:
            return None

        soup = BeautifulSoup(html_content, 'html.parser')

        # 1. ดึงชื่อหนังสือ (ค้นหาจาก tag h1 หรือ title)
        h1_tag = soup.find('h1')
        book_title = h1_tag.get_text(strip=True) if h1_tag else soup.title.string

        # 2. ดึงรายชื่อบทเรียน (ค้นหาลิงก์ในหน้าสารบัญ)
        chapter_titles = []
        
        # ค้นหาลิงก์บทเรียนตามโครงสร้างหน้าเว็บปัจจุบัน
        links = soup.find_all('a')
        for link in links:
            text = link.get_text(strip=True)
            # กรองเฉพาะลิงก์ที่มีคำว่า Chapter หรือ Part
            if text and ('Chapter' in text or 'Part' in text):
                if text not in chapter_titles:
                    chapter_titles.append(text)

        return {
            "book_title": book_title,
            "chapter_titles": chapter_titles
        }