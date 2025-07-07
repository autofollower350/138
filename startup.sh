#!/bin/bash

echo "📦 Installing Python packages..."
pip install -r requirements.txt

echo "📦 Installing Chrome and ChromeDriver..."

mkdir -p .chrome
mkdir -p .chromedriver

# Install Chrome
wget -q https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.113/linux64/chrome-linux64.zip
unzip -q chrome-linux64.zip
mv chrome-linux64/chrome .chrome/chrome

# Install ChromeDriver
wget -q -O chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.113/linux64/chromedriver-linux64.zip
unzip -q chromedriver.zip
mv chromedriver-linux64/chromedriver .chromedriver/chromedriver
chmod +x .chromedriver/chromedriver

echo "✅ Chrome and ChromeDriver installed"
