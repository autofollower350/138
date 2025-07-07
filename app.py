import os
import tempfile
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_path = os.path.abspath(".chrome/chrome")
chromedriver_path = os.path.abspath(".chromedriver/chromedriver")

if not os.path.exists(chrome_path):
    raise Exception("❌ Chrome not found at: " + chrome_path)
if not os.path.exists(chromedriver_path):
    raise Exception("❌ ChromeDriver not found at: " + chromedriver_path)

options = Options()
options.binary_location = chrome_path
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 🔥 FIX: unique user-data-dir
user_data_dir = tempfile.mkdtemp()
options.add_argument(f"--user-data-dir={user_data_dir}")

# Launch Chrome
driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
driver.get("https://www.google.com")
print("✅ Opened:", driver.title)

driver.quit()
shutil.rmtree(user_data_dir, ignore_errors=True)
