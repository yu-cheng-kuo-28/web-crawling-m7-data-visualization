#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

ticker = 'NVDA'
url = f"https://stockanalysis.com/stocks/{ticker.lower()}/statistics/"

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')

driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

print(f"Loading {ticker} from StockAnalysis.com...")
time.sleep(3)

# Get body text
body_text = driver.find_element(By.TAG_NAME, 'body').text
lines = body_text.split('\n')

print(f"Found {len(lines)} lines of text\n")

# Show lines around "Valuation Ratios"
for i, line in enumerate(lines):
    if 'Valuation Ratios' in line:
        print(f"Found 'Valuation Ratios' at line {i}")
        print("\nLines around it:")
        for j in range(max(0, i-2), min(len(lines), i+25)):
            print(f"  [{j}] {lines[j]}")
        break

# Look for PE Ratio specifically
print("\n" + "="*60)
print("Looking for PE Ratio...")
for i, line in enumerate(lines):
    if line.strip() == 'PE Ratio' and i + 1 < len(lines):
        print(f"Found at line {i}: '{line}'")
        print(f"Next line [{i+1}]: '{lines[i+1]}'")

driver.quit()
