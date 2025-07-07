import os
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_path = os.path.abspath(".chrome/chrome")
chromedriver_path = os.path.abspath(".chromedriver/chromedriver")

# Check paths exist
if not os.path.exists(chrome_path):
    raise Exception("❌ Chrome not found at: " + chrome_path)

if not os.path.exists(chromedriver_path):
    raise Exception("❌ ChromeDriver not found at: " + chromedriver_path)

# Create temp user data dir to avoid session conflicts
user_data_dir = tempfile.mkdtemp()

# Setup Chrome options
options = Options()
options.binary_location = chrome_path
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument(f"--user-data-dir={user_data_dir}")

# Start Chrome
driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
driver.get("https://www.google.com")
print("✅ Page Title:", driver.title)
driver.quit()
