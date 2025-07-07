#!/bin/bash

echo "📦 Installing Chrome and ChromeDriver..."

# Chrome install
mkdir -p .chrome
wget -q https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.113/linux64/chrome-linux64.zip
unzip -q chrome-linux64.zip
mv chrome-linux64/* .chrome/

# ChromeDriver install
mkdir -p .chromedriver
wget -q -O chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.113/linux64/chromedriver-linux64.zip
unzip -q chromedriver.zip
mv chromedriver-linux64/chromedriver .chromedriver/
chmod +x .chromedriver/chromedriver

echo "✅ Chrome and ChromeDriver installed to project folder"
