#!/bin/bash

echo "📦 Installing Python dependencies..."
pip install selenium

echo "📦 Installing Chrome and ChromeDriver..."

# Create local bin dirs inside project dir
mkdir -p .chrome
mkdir -p .chromedriver

# Download and extract Chrome
wget -q https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.113/linux64/chrome-linux64.zip
unzip -q chrome-linux64.zip
mv chrome-linux64/chrome .chrome/chrome

# Download and extract ChromeDriver
wget -q -O chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.113/linux64/chromedriver-linux64.zip
unzip -q chromedriver.zip
mv chromedriver-linux64/chromedriver .chromedriver/chromedriver
chmod +x .chromedriver/chromedriver

echo "✅ Chrome and ChromeDriver installed to project folder"
ls -l .chrome/chrome
ls -l .chromedriver/chromedriver
