Markdown

# Week 14: Advanced Web Scraping & Introduction to Automated Agents
This project builds a more advanced, "agentic" web scraper using `Selenium` for dynamic
content and a configuration-driven approach for adaptability. It demonstrates how to automate
Browse, extract structured data, handle pagination, and manage data persistence.
## Key Concepts Demonstrated

* **Selenium for Dynamic Content**: Using a real browser (headless or visible) to interact with
JavaScript-rendered web pages.
* **WebDriver Management**: Automated setup of browser drivers using `webdriver_manager`.
* **Config-Driven Automation**: The scraper's behavior (what to scrape, how to paginate) is
defined in an external JSON configuration file, allowing it to adapt to different websites without
code changes.
* **Modular Agent Design**: Breaking down the scraping logic into specialized modules
(`scraper_agent`, `config_parser`, `data_models`, `utils`, `driver_manager`).
* **Robustness**: Implementing explicit waits, retry mechanisms for clicks, and basic error
handling for network/element issues.
* **Structured Data**: Parsing extracted information into Python dataclasses and saving it to
JSON.
## Ethical and Legal Considerations
**It is crucial to understand and adhere to ethical and legal guidelines when web scraping:**
* **`robots.txt`**: Always check a website's `robots.txt` file (e.g., `https://example.com/robots.txt`)
before scraping. This file specifies which parts of the site can be crawled by bots.
* **Terms of Service (ToS)**: Review the website's Terms of Service. Many sites explicitly forbid
scraping.
* **Rate Limiting**: Do not overwhelm the website's server with too many requests too quickly.
Use `time.sleep()` or built-in Selenium waits (as done in `scraper_agent.py`) to introduce delays.
* **Data Usage**: Be aware of intellectual property rights. You generally cannot republish
scraped content without permission.
* **Legality**: Web scraping legality varies by jurisdiction and case. Always err on the side of
caution. **This project is for educational purposes only.**
## Setup & How to Run
1. **Clone the repository:**
```bash
git clone
[https://github.com/YOUR_USERNAME/agentic-web-scraper.git](https://github.com/YOUR_USERNAME/a
gentic-web-scraper.git)
cd agentic-web-scraper
```
2. **Install Dependencies:**
It's highly recommended to use a virtual environment:
```bash
python -m venv venv

source venv/bin/activate # On Windows: venv\Scripts\activate.bat
pip install selenium beautifulsoup4 webdriver-manager
```
3. **Ensure Browser and WebDriver are compatible:**
* The `driver_manager.py` uses `webdriver_manager` to automatically download the correct
WebDriver.
* Make sure you have either **Google Chrome** or **Mozilla Firefox** installed on your system, as
these are the browsers `Selenium` will control.
4. **Configure `configs/example_site_config.json`:**
* This file dictates what and how the scraper will extract. The provided example is configured for
`books.toscrape.com`. You can modify it to target other simple sites (be respectful!).
* **Crucially, adjust selectors based on the target website's HTML structure.** Use your browser's
Developer Tools (F12) to inspect elements.
5. **Run the scraper:**
```bash
python main.py
```
The scraper will launch a browser (headless by default), navigate the pages, extract data, and save it to
`data/scraped_products.json`.
## Project Structure

agentic-web-scraper/
├── src/
│ ├── init.py # Python package marker
│ ├── scraper_agent.py # Main logic: reads config, navigates, extracts, paginates
│ ├── config_parser.py # Loads and validates JSON configurations
│ ├── data_models.py # Python classes for structured scraped data
│ ├── utils.py # Helper functions (save data, waits, robust clicks)
│ └── driver_manager.py # Handles Selenium WebDriver setup and teardown
├── configs/
│ └── example_site_config.json # Site-specific scraping rules
├── data/
│ └── scraped_products.json # Output file for scraped data
├── main.py # Application entry point
├── .gitignore # Files/folders to ignore in Git
├── README.md # This project overview
└── docs/
└── ETHICS.md # Important document on ethical & legal scraping

## Debugging Advanced Web Scraping
* **WebDriver Errors**: `WebDriverException`, `SessionNotCreatedException`. Often means
the WebDriver is not found, or its version is incompatible with your browser. Ensure
`webdriver-manager` is installed and updated, and your browser is up-to-date.
* **Element Not Found (`NoSuchElementException`)**: Your CSS selector or XPath is incorrect,
or the element hasn't loaded yet.
* **Solution**: Use browser DevTools (F12) to re-verify selectors. Implement explicit waits
(`WebDriverWait`) to ensure elements are present and visible before trying to interact.
* **Timeout Errors (`TimeoutException`)**: The element you are waiting for did not appear
within the specified time.
* **Solution**: Increase wait times, or inspect the website's loading behavior. Is it genuinely
slow, or is the element truly not appearing?
* **Stale Element Reference (`StaleElementReferenceException`)**: An element you previously
found is no longer attached to the DOM (e.g., after a page refresh or dynamic update).
* **Solution**: Re-find the element after actions that might change the DOM (like a page load
or AJAX update).
* **Infinite Pagination Loops**: The "next page" selector always finds something, even on the
last page, or clicks the wrong element.
* **Solution**: Carefully inspect the "next page" button on the last page. Does its selector
change? Does it become disabled? Implement checks for these conditions.
* **Anti-Bot Measures**: Websites may detect automated access and block you (e.g.,
CAPTCHAs, IP bans).
* **Solution**: Start with slow delays (`time.sleep()`), use realistic User-Agents, consider
rotating IPs (advanced topic). For this week, prioritize understanding the mechanism over
bypassing sophisticated defenses.
* **Headless vs. Headed**: If you encounter issues in headless mode, try running with
`headless=False` in `main.py` to visually debug what the browser is doing.
## Extension Ideas (Future Work)
* **More Robust Anti-Blocking**: Integrate proxy rotation, solve simple CAPTCHAs (using
external services), or implement more sophisticated User-Agent rotation strategies.
* **Data Pipelines**: Integrate with databases (SQLite, PostgreSQL), data lakes, or cloud
storage.
* **Error Reporting & Monitoring**: Implement detailed logging, email notifications for failures,
or dashboarding.
* **Concurrent Scraping**: Use `threading` or `asyncio` to scrape multiple pages or items
concurrently (with careful rate limiting).
* **Advanced AI Integration**:

* **LLM-driven Selector Generation**: Use an LLM to "understand" the page structure and
*generate* CSS/XPath selectors based on natural language descriptions (e.g., "get the price of
the main product").
* **Adaptive Navigation**: An LLM could decide *where to click next* based on a high-level
goal and observed page content.
* **Failure Recovery**: AI could analyze scraping failures (e.g., element not found) and
suggest alternative selectors or actions.
* **GUI for Configuration**: Build a simple GUI that allows users to create and manage scraping
configurations visually.
* **Scheduled Scraping**: Integrate with tools like `cron` (Linux) or Windows Task Scheduler to
run the scraper automatically at intervals.
---
#### **11. `agentic-web-scraper/docs/ETHICS.md`**
```markdown
# Web Scraping Ethics and Legality Guidelines
This document outlines important ethical and legal considerations when engaging in web
scraping. It is crucial to understand and adhere to these principles to avoid legal issues, IP
blocking, or causing harm to website owners.
## 1. Respect `robots.txt`
The `robots.txt` file is a standard that websites use to communicate with web crawlers and
scrapers. It tells bots which parts of the site they are allowed to access and which parts are
forbidden.
* **Always check:** Before scraping any website, visit `https://[website-domain]/robots.txt`
(e.g., `https://example.com/robots.txt`).
* **Adhere to rules:** If `robots.txt` disallows scraping a certain path, **do not scrape it**. This
is a direct request from the website owner.
## 2. Review Terms of Service (ToS)
Many websites include clauses in their Terms of Service that explicitly prohibit web scraping,
data mining, or automated access.
* **Read the fine print:** If a website's ToS explicitly forbids scraping, then scraping that site is a
breach of contract and could lead to legal action (e.g., Cease and Desist letters, lawsuits).
* **Implied consent:** Absence of a specific prohibition does not automatically grant

permission.
## 3. Be Polite: Rate Limiting and Delays
Overwhelming a website's server with too many requests in a short period can be interpreted
as a Denial-of-Service (DoS) attack, impacting the site's performance for legitimate users.
* **Introduce Delays:** Use `time.sleep()` between requests or pages to mimic human Browse
behavior. A delay of 2-5 seconds is a common starting point, but adjust based on the site's
load.
* **Avoid Concurrent Requests:** Unless you know what you are doing and have explicit
permission, avoid sending multiple requests simultaneously.
* **Monitor Server Load:** If you notice slower response times or errors, reduce your request
rate.
## 4. Identify Yourself (User-Agent)
When making requests, include a descriptive `User-Agent` header that identifies your scraper.
This allows website administrators to contact you if there are issues.
* **Example:** `Mozilla/5.0 (compatible; MyCustomScraper/1.0;
mailto:your_email@example.com)`
* **Avoid generic agents:** Do not impersonate common browsers or Googlebot unless your
scraper genuinely behaves like them and respects their rules.
## 5. Do Not Impersonate or Hide (Ethically)
While some advanced anti-bot measures might necessitate techniques like rotating IP
addresses or using headless browsers, prioritize ethical considerations:
* **Transparency:** If possible, be transparent about your scraping activities.
* **Avoid malicious intent:** Do not use scraped data for illegal activities, spam, or competitive
disadvantage where it violates the ToS.
## 6. Data Usage and Copyright
* **Copyright:** Scraped content is often copyrighted. You generally cannot republish,
distribute, or monetize scraped data without explicit permission from the copyright holder.
* **Fair Use:** Understand your local "fair use" (or similar) doctrines, but these are often narrow
and context-dependent.
* **Personal Use:** Scraping for personal, non-commercial use (e.g., research, personal

archive) is generally less risky but still subject to ToS.
## 7. Legal Precedents and Risks
The legal landscape for web scraping is evolving and varies by country. Notable cases exist
where scraping has been deemed illegal, particularly when it involves:
* Breaching ToS / contract.
* Trespass to chattels (unauthorized access to computer systems causing harm).
* Copyright infringement.
* Data privacy violations (e.g., scraping personal identifiable information (PII) without consent).
**In summary, always act responsibly, respectfully, and legally. When in doubt, seek explicit
permission from the website owner.**
---