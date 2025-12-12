#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

ticker = 'AAPL'
url = f"https://www.nasdaq.com/market-activity/stocks/{ticker.lower()}/price-earnings-peg-ratios"

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--log-level=3')

driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

print(f"Loading {ticker}...")
time.sleep(5)

divs = driver.find_elements(By.TAG_NAME, 'div')
print(f"Found {len(divs)} divs")

found = False
for div in divs:
    try:
        text = div.text.strip()
        if 'Price/Earnings Ratio' in text and '2024 Actual' in text and len(text) < 1000:
            print(f"\nFound data section:\n{text}\n")
            found = True
            break
    except:
        pass

if not found:
    print("Could not find Price/Earnings Ratio section")
    print("\nSearching for any PEG mentions...")
    for div in divs[:100]:
        try:
            text = div.text.strip()
            if 'PEG' in text and len(text) < 200:
                print(f"  - {text[:100]}")
        except:
            pass

driver.quit()
