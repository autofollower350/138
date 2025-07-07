import nest_asyncio
nest_asyncio.apply()

import os
import time
import shutil
import tempfile
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# CONFIG
API_ID = 28590286
API_HASH = "6a68cc6b41219dc57b7a52914032f92f"
BOT_TOKEN = "7412939071:AAFgfHJGhMXw9AuGAAnPuGk_LbAlB5kX2KY"
DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# GLOBALS
driver = None
user_data_dir = None

# Initialize bot
app = Client("jnvu_result_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    global driver, user_data_dir

    await message.reply("🔄 Starting browser session...")

    if driver is None:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.binary_location = os.path.abspath(".chrome/chrome")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # ✅ Create unique temp folder for Chrome profile
        user_data_dir = tempfile.mkdtemp()
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        })

        # Launch browser
        driver = webdriver.Chrome(
            service=Service(os.path.abspath(".chromedriver/chromedriver")),
            options=chrome_options
        )

        driver.get("https://share.google/RiGoUdAWQEkczypqg")
        time.sleep(2)
        driver.find_element(By.XPATH, "/html/body/form/div[3]/div/div[1]/fieldset/div/div[1]/div/div[1]/table/tbody/tr[2]/td/div/div/ul/li[1]/span[3]/a").click()
        time.sleep(2)
        driver.find_element(By.XPATH, "/html/body/form/div[3]/div/div/fieldset/div/div[3]/div/div/div/table/tbody/tr[2]/td/div/ul/div/table/tbody/tr[2]/td[2]/span[1]/a").click()
        time.sleep(2)

        await message.reply("✅ Bot is ready! Now send your roll number like `25rba00299`.")


@app.on_message(filters.text & filters.private & ~filters.command(["start", "help"]))
async def handle_roll_number(client: Client, message: Message):
    global driver
    roll_number = message.text.strip()

    if not (6 <= len(roll_number) <= 15 and roll_number.isalnum()):
        await message.reply("⚠️ Invalid roll number. Use lowercase like `25rba00299`")
        return

    if driver is None:
        await message.reply("⚠️ Browser not initialized. Send /start first.")
        return

    try:
        # Clear old PDFs
        for f in os.listdir(DOWNLOAD_DIR):
            if f.endswith(".pdf"):
                os.remove(os.path.join(DOWNLOAD_DIR, f))

        # Enter roll number
        input_field = driver.find_element(By.XPATH, "/html/body/form/div[4]/div/div[2]/table/tbody/tr/td[2]/span/input")
        input_field.clear()
        input_field.send_keys(roll_number)
        time.sleep(1)

        # Submit form
        driver.find_element(By.XPATH, "/html/body/form/div[4]/div/div[3]/span[1]/input").click()
        time.sleep(3)

        # Wait for download
        timeout = 5
        pdf_path = None
        for _ in range(timeout):
            pdf_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".pdf")]
            if pdf_files:
                pdf_path = os.path.join(DOWNLOAD_DIR, pdf_files[0])
                break
            time.sleep(1)

        if pdf_path and os.path.exists(pdf_path):
            driver.refresh()
            time.sleep(2)
            await message.reply_document(pdf_path, caption=f"📄 Result PDF for Roll Number: `{roll_number}`")
        else:
            await message.reply("⚠️ Result PDF not found. Please check the roll number or try again later.")

    except Exception as e:
        await message.reply(f"❌ Error: `{str(e)}`")


# Start bot
async def main():
    await app.start()
    print("✅ Bot is running...")
    await asyncio.Event().wait()

try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    print("🛑 Stopping bot...")
finally:
    if driver:
        driver.quit()
    if user_data_dir:
        shutil.rmtree(user_data_dir, ignore_errors=True)
