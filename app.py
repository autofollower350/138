import nest_asyncio
nest_asyncio.apply()

import os
import time
import shutil
import tempfile
import asyncio
import uvicorn

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

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

# FastAPI app
web_app = FastAPI()

@web_app.get("/", response_class=PlainTextResponse)
async def root():
    return "✅ JNVU Result Bot is Alive!"

# Telegram Bot
bot = Client("jnvu_result_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    global driver, user_data_dir

    await message.reply("🚀 Starting bot...")

    if driver is None:
        chrome_options = Options()
        chrome_options.binary_location = os.path.abspath(".chrome/chrome")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        user_data_dir = tempfile.mkdtemp()
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        })

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

@bot.on_message(filters.text & filters.private & ~filters.command(["start", "help"]))
async def handle_roll_number(client: Client, message: Message):
    global driver
    text = message.text.strip().lower().replace(" ", "")

    if driver is None:
        await message.reply("⚠️ Browser not initialized. Send /start first.")
        return

    roll_numbers = []

    if "-" in text:
        try:
            start_part, end_part = text.split("-")

            import re
            match1 = re.match(r"([a-zA-Z0-9]+?)(\d+)$", start_part)
            match2 = re.match(r"([a-zA-Z0-9]+?)(\d+)$", end_part)

            if not match1 or not match2:
                await message.reply("⚠️ Invalid roll number format.")
                return

            prefix_start, num_start = match1.groups()
            prefix_end, num_end = match2.groups()

            if prefix_start != prefix_end:
                await message.reply("⚠️ Prefixes do not match in range.")
                return

            start_num = int(num_start)
            end_num = int(num_end)
            digit_length = len(num_start)

            if end_num < start_num or (end_num - start_num) > 1000:
                await message.reply("⚠️ Invalid range or too large (max 1000).")
                return

            roll_numbers = [f"{prefix_start}{str(i).zfill(digit_length)}" for i in range(start_num, end_num + 1)]
            await message.reply(f"🔍 Fetching results for {len(roll_numbers)} roll numbers. Please wait...")

        except Exception:
            await message.reply("⚠️ Invalid range format. Use like `25rba00001-25rba00010`")
            return

    else:
        if not (6 <= len(text) <= 15 and text.isalnum()):
            await message.reply("⚠️ Invalid roll number. Use lowercase like `25rba00299`")
            return
        roll_numbers = [text]

    for roll_number in roll_numbers:
        try:
            for f in os.listdir(DOWNLOAD_DIR):
                if f.endswith(".pdf"):
                    os.remove(os.path.join(DOWNLOAD_DIR, f))

            input_field = driver.find_element(By.XPATH, "/html/body/form/div[4]/div/div[2]/table/tbody/tr/td[2]/span/input")
            input_field.clear()
            input_field.send_keys(roll_number)
            time.sleep(1)

            driver.find_element(By.XPATH, "/html/body/form/div[4]/div/div[3]/span[1]/input").click()
            time.sleep(3)

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
                await message.reply(f"❌ PDF not found for `{roll_number}`")

        except Exception as e:
            await message.reply(f"❌ Error for `{roll_number}`: `{str(e)}`")

# Launch both: bot + FastAPI server
async def main():
    await bot.start()
    print("✅ Telegram bot started")

    config = uvicorn.Config(web_app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), log_level="info")
    server = uvicorn.Server(config)

    # Run FastAPI and bot in parallel
    await asyncio.gather(
        server.serve(),
    )

try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    print("🛑 Shutting down...")
finally:
    if driver:
        driver.quit()
    if user_data_dir:
        shutil.rmtree(user_data_dir, ignore_errors=True)
