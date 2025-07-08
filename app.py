import nest_asyncio
nest_asyncio.apply()

import os
import time
import shutil
import tempfile
import asyncio
import zipfile
import re

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

    await message.reply("馃攧 Starting bro...")

    if driver is None:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.binary_location = os.path.abspath(".chrome/chrome")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # 鉁� Create unique temp folder for Chrome profile
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

        await message.reply("鉁� Bot is ready! Now send your roll number like `25rba00299`.")

@app.on_message(filters.text & filters.private & ~filters.command(["start", "help"]))
async def handle_roll_number(client: Client, message: Message):
    global driver
text = re.sub(r"[^\w\-]", "", message.text.strip().lower())
    roll_numbers = []

    if driver is None:
        await message.reply("⚠️ Browser not initialized. Send /start first.")
        return

    # ✅ Range input
    if "-" in text:
        try:
            start_part, end_part = text.split("-")

            import re
            match1 = re.match(r"([a-zA-Z]+)(\d+)$", start_part)
            match2 = re.match(r"([a-zA-Z]+)(\d+)$", end_part)

            if not match1 or not match2:
                await message.reply("⚠️ Invalid roll number format.")
                return

            prefix_start, num_start = match1.groups()
            prefix_end, num_end = match2.groups()

            if prefix_start != prefix_end:
                await message.reply("⚠️ Prefix mismatch in range.")
                return

            start_num = int(num_start)
            end_num = int(num_end)
            digit_length = len(num_start)

            if end_num < start_num or (end_num - start_num) > 500:
                await message.reply("⚠️ Invalid range or too large (max 500).")
                return

            roll_numbers = [f"{prefix_start}{str(i).zfill(digit_length)}" for i in range(start_num, end_num + 1)]
            await message.reply(f"🔄 Processing {len(roll_numbers)} roll numbers. Please wait...")
        except:
            await message.reply("⚠️ Invalid format. Use like `25rba00001-25rba00050`.")
            return

    else:
        if not (6 <= len(text) <= 15 and text.isalnum()):
            await message.reply("⚠️ Invalid roll number.")
            return
        roll_numbers = [text]

    # 🧹 Clean old files
    for f in os.listdir(DOWNLOAD_DIR):
        os.remove(os.path.join(DOWNLOAD_DIR, f))

    success_count = 0
    for roll_number in roll_numbers:
        try:
            # Remove existing named file
            final_path = os.path.join(DOWNLOAD_DIR, f"{roll_number}.pdf")
            if os.path.exists(final_path):
                os.remove(final_path)

            # 🖊️ Enter roll number
            input_field = driver.find_element(By.XPATH, "/html/body/form/div[4]/div/div[2]/table/tbody/tr/td[2]/span/input")
            input_field.clear()
            input_field.send_keys(roll_number)
            time.sleep(1)

            # Submit
            driver.find_element(By.XPATH, "/html/body/form/div[4]/div/div[3]/span[1]/input").click()
            time.sleep(3)

            # Wait for PDF
            timeout = 5
            pdf_path = None
            for _ in range(timeout):
                pdf_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".pdf")]
                if pdf_files:
                    pdf_path = os.path.join(DOWNLOAD_DIR, pdf_files[0])
                    break
                time.sleep(1)

            if pdf_path and os.path.exists(pdf_path):
                new_pdf_path = os.path.join(DOWNLOAD_DIR, f"{roll_number}.pdf")
                os.rename(pdf_path, new_pdf_path)
                success_count += 1
                driver.refresh()
                time.sleep(1)
            else:
                await message.reply(f"❌ PDF not found for `{roll_number}`")

        except Exception as e:
            await message.reply(f"❌ Error for `{roll_number}`: `{str(e)}`")

    if success_count == 0:
        await message.reply("⚠️ कोई भी PDF नहीं मिली।")
        return

    # ✅ Create ZIP file
    zip_path = os.path.join("/tmp", f"results_{roll_numbers[0]}_to_{roll_numbers[-1]}.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for f in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, f)
            zipf.write(file_path, arcname=f)

    await message.reply_document(zip_path, caption=f"📦 {success_count} PDFs zipped.\n🧾 Range: `{roll_numbers[0]} - {roll_numbers[-1]}`")

#start
async def main():
    await app.start()
    print("鉁� Bot is running...")
    await asyncio.Event().wait()

try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    print("馃洃 Stopping bot...")
finally:
    if driver:
        driver.quit()
    if user_data_dir:
        shutil.rmtree(user_data_dir, ignore_errors=True)
