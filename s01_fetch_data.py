#!/usr/bin/env python3
"""
Fetch valuation measures for the Magnificent 7 from multiple sources:
  - Yahoo Finance (via yfinance API)
  - StockAnalysis.com (via Selenium web scraping)

Export:
  1) valuation_measures_full.csv  (all periods, tidy format)
  2) valuation_measures_current.csv  (only "Current" values, wide format)
"""

import time
import os
from datetime import datetime
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import yaml


def load_tickers_from_config() -> List[str]:
    """Load stock tickers from config/01_config_fetch.yaml file."""
    config_file = 'config/01_config_fetch.yaml'
    
    if not os.path.exists(config_file):
        # Fallback to Magnificent 7 if config doesn't exist
        print(f"Warning: {config_file} not found, using default Magnificent 7 tickers")
        return ["AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA", "TSLA"]
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    tickers = config.get('tickers', [])
    if not tickers:
        print(f"Warning: No tickers found in {config_file}, using default Magnificent 7 tickers")
        return ["AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA", "TSLA"]
    
    return tickers


def load_term_conversion_table() -> Dict[str, Dict[str, str]]:
    """
    Load the term conversion table to map source-specific terms to consolidated terms.
    Returns a dict with 'yahoo_finance' and 'stockanalysis' mappings.
    """
    conversion_file = 'tool/term_conversion_table.csv'
    
    if not os.path.exists(conversion_file):
        # Return empty mappings if file doesn't exist
        return {'yahoo_finance': {}, 'stockanalysis': {}}
    
    df = pd.read_csv(conversion_file, skipinitialspace=True)
    
    # Create mapping dictionaries
    yahoo_to_consolidated = {}
    sa_to_consolidated = {}
    
    for _, row in df.iterrows():
        consolidated = row['consolidated_term'].strip()
        yahoo_term = row['yahoo_finance'].strip()
        sa_term = row['stock_analysis'].strip()
        
        yahoo_to_consolidated[yahoo_term] = consolidated
        sa_to_consolidated[sa_term] = consolidated
    
    return {
        'yahoo_finance': yahoo_to_consolidated,
        'stockanalysis': sa_to_consolidated
    }


def fetch_yahoo_finance_data(ticker_symbol: str) -> Optional[Dict[str, any]]:
    """
    Fetch valuation measures for a ticker using yfinance API.
    Returns a dictionary of valuation metrics.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        # Extract valuation measures
        measures = {
            "Market Cap": info.get('marketCap'),
            "Enterprise Value": info.get('enterpriseValue'),
            "Trailing P/E": info.get('trailingPE'),
            "Forward P/E": info.get('forwardPE'),
            "PEG Ratio (5yr expected)": info.get('trailingPegRatio'),  # Fixed: use trailingPegRatio
            "Price/Sales (ttm)": info.get('priceToSalesTrailing12Months'),
            "Price/Book (mrq)": info.get('priceToBook'),
            "Enterprise Value/Revenue": info.get('enterpriseToRevenue'),
            "Enterprise Value/EBITDA": info.get('enterpriseToEbitda'),
        }
        
        return measures
    except Exception as e:
        print(f"  ERROR fetching Yahoo data for {ticker_symbol}: {e}")
        return None


def fetch_stockanalysis_data(ticker_symbol: str) -> Optional[Dict[str, any]]:
    """
    Fetch valuation ratios from StockAnalysis.com using Selenium.
    Fetches: PE Ratio, Forward PE, PS Ratio, PB Ratio, PEG Ratio
    """
    driver = None
    try:
        url = f"https://stockanalysis.com/stocks/{ticker_symbol.lower()}/statistics/"
        
        # Setup Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--log-level=3')  # Suppress logs
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait for JavaScript to render
        time.sleep(3)
        
        # Initialize measures (using names that match StockAnalysis website)
        measures = {
            "PE Ratio": None,
            "Forward PE": None,
            "PS Ratio": None,
            "PB Ratio": None,
            "PEG Ratio": None,
        }
        
        # Get the page text
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        
        # Parse the valuation ratios section
        lines = page_text.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            
            try:
                # StockAnalysis format: "PE Ratio 45.49" (label and value on same line)
                parts = line_stripped.split()
                
                # PE Ratio
                if line_stripped.startswith('PE Ratio ') and len(parts) == 3:
                    measures["PE Ratio"] = float(parts[2])
                
                # Forward PE
                elif line_stripped.startswith('Forward PE ') and len(parts) == 3:
                    measures["Forward PE"] = float(parts[2])
                
                # PS Ratio
                elif line_stripped.startswith('PS Ratio ') and len(parts) == 3:
                    measures["PS Ratio"] = float(parts[2])
                
                # PB Ratio
                elif line_stripped.startswith('PB Ratio ') and len(parts) == 3:
                    measures["PB Ratio"] = float(parts[2])
                
                # PEG Ratio
                elif line_stripped.startswith('PEG Ratio ') and len(parts) == 3:
                    measures["PEG Ratio"] = float(parts[2])
            
            except (ValueError, AttributeError, IndexError):
                continue
        
        return measures
        
    except Exception as e:
        print(f"  WARNING: Could not fetch StockAnalysis data for {ticker_symbol}: {e}")
        # Return structure with N/A values
        return {
            "PE Ratio": None,
            "Forward PE": None,
            "PS Ratio": None,
            "PB Ratio": None,
            "PEG Ratio": None,
        }
    finally:
        if driver:
            driver.quit()


def format_large_number(num: Optional[float]) -> str:
    """
    Format large numbers in a human-readable way (e.g., 3.87T, 245.12B, 1.23M)
    """
    if num is None or pd.isna(num):
        return "N/A"
    
    try:
        num = float(num)
        if num >= 1_000_000_000_000:  # Trillions
            return f"{num / 1_000_000_000_000:.2f}T"
        elif num >= 1_000_000_000:  # Billions
            return f"{num / 1_000_000_000:.2f}B"
        elif num >= 1_000_000:  # Millions
            return f"{num / 1_000_000:.2f}M"
        else:
            return f"{num:.2f}"
    except (ValueError, TypeError):
        return str(num)


def crawl_magnificent7() -> None:
    """
    Main driver:
      - Loop tickers
      - Fetch valuation measures from Yahoo Finance and StockAnalysis
      - Consolidate terms using conversion table
      - Accumulate data in tidy format
      - Save:
          1) valuation_measures_full.csv (tidy format)
          2) valuation_measures_current.csv (wide format)
    """
    all_data: List[Dict] = []
    failed: List[str] = []
    
    # Get current date for the fetch timestamp
    fetch_date = datetime.now().strftime('%Y-%m-%d')
    
    # Load term conversion table
    term_mappings = load_term_conversion_table()
    
    # Load tickers from config
    tickers = load_tickers_from_config()
    print(f"\n📋 Loaded {len(tickers)} tickers from config: {', '.join(tickers)}")
    
    # Check which tickers already have data for today
    csv_dir = 'csv'
    full_csv = os.path.join(csv_dir, "valuation_measures_full.csv")
    
    existing_tickers_today = set()
    if os.path.exists(full_csv):
        existing_full_df = pd.read_csv(full_csv)
        if not existing_full_df.empty:
            today_data = existing_full_df[existing_full_df['Fetch_Date'] == fetch_date]
            if not today_data.empty:
                # Get unique tickers that have data from BOTH sources for today
                ticker_counts = today_data.groupby('Ticker')['Data_Source'].nunique()
                existing_tickers_today = set(ticker_counts[ticker_counts == 2].index)
                
                if existing_tickers_today:
                    print(f"\n✓ Found existing data for {fetch_date}: {', '.join(sorted(existing_tickers_today))}")
    
    # Filter to only fetch missing tickers
    tickers_to_fetch = [t for t in tickers if t not in existing_tickers_today]
    
    if not tickers_to_fetch:
        print(f"\n✓ All {len(tickers)} tickers already have data for {fetch_date}")
        print("  Nothing to fetch. Delete specific ticker rows if you want to re-fetch.")
        return
    
    if existing_tickers_today:
        print(f"\n📋 Will fetch {len(tickers_to_fetch)} missing tickers: {', '.join(tickers_to_fetch)}")
    
    tickers = tickers_to_fetch
    
    # Fetch from both Yahoo Finance and StockAnalysis (missing tickers only)
    for ticker in tickers:
        print(f"\n{'='*60}")
        print(f"Processing {ticker}")
        print(f"{'='*60}")
        
        try:
            # 1. Fetch from Yahoo Finance
            print(f"  [1/2] Fetching from Yahoo Finance...")
            yahoo_measures = fetch_yahoo_finance_data(ticker)
            if yahoo_measures is None:
                print(f"  !! Could not fetch Yahoo data for {ticker}")
            else:
                # Convert to tidy format with consolidated terms
                for measure_name, value in yahoo_measures.items():
                    # Use consolidated term if available, otherwise keep original
                    consolidated_term = term_mappings['yahoo_finance'].get(measure_name, measure_name)
                    
                    all_data.append({
                        "Fetch_Date": fetch_date,
                        "Data_Source": "yahoo_finance",
                        "Ticker": ticker,
                        "Measure": consolidated_term,
                        "Value_Raw": value,
                        "Value_Formatted": format_large_number(value) if measure_name in ["Market Cap", "Enterprise Value"] else (f"{value:.2f}" if value is not None and not pd.isna(value) else "N/A")
                    })
                print(f"  ✓ Yahoo Finance data fetched")
            
            time.sleep(0.5)  # Be polite to Yahoo Finance API
            
            # 2. Fetch from StockAnalysis
            print(f"  [2/2] Fetching from StockAnalysis.com...")
            stockanalysis_measures = fetch_stockanalysis_data(ticker)
            if stockanalysis_measures is None:
                print(f"  !! Could not fetch StockAnalysis data for {ticker}")
            else:
                # Convert to tidy format with consolidated terms
                for measure_name, value in stockanalysis_measures.items():
                    # Use consolidated term if available, otherwise keep original
                    consolidated_term = term_mappings['stockanalysis'].get(measure_name, measure_name)
                    
                    all_data.append({
                        "Fetch_Date": fetch_date,
                        "Data_Source": "stockanalysis",
                        "Ticker": ticker,
                        "Measure": consolidated_term,
                        "Value_Raw": value,
                        "Value_Formatted": format_large_number(value) if consolidated_term in ["Market Cap", "Enterprise Value"] else (f"{value:.2f}" if value is not None and not pd.isna(value) else "N/A")
                    })
                # Check if we got any actual data
                has_data = any(v is not None and not pd.isna(v) for v in stockanalysis_measures.values())
                if has_data:
                    print(f"  ✓ StockAnalysis data fetched successfully")
                else:
                    print(f"  ⚠ StockAnalysis data fetched but all values are N/A")
            
            time.sleep(1.0)  # Be polite to StockAnalysis
            
            print(f"✓ Completed {ticker}")
            
        except Exception as e:
            print(f"  ERROR on {ticker}: {e}")
            failed.append(ticker)

    if not all_data:
        print("No data fetched. Nothing to save.")
        return

    # Create tidy DataFrame for new data
    new_df = pd.DataFrame(all_data)

    # Create csv directory if it doesn't exist
    csv_dir = 'csv'
    os.makedirs(csv_dir, exist_ok=True)

    # Load existing full dataset and append new data
    full_csv = os.path.join(csv_dir, "valuation_measures_full.csv")
    if os.path.exists(full_csv):
        existing_df = pd.read_csv(full_csv)
        # Append new data to existing
        full_df = pd.concat([existing_df, new_df], ignore_index=True)
        print(f"\n[1] Appended new data to existing {full_csv}")
        print(f"    Total records: {len(existing_df)} → {len(full_df)} (+{len(new_df)} new)")
    else:
        full_df = new_df
        print(f"\n[1] Created new {full_csv}")
    
    # Save combined dataset
    full_df.to_csv(full_csv, index=False)
    print(f"    Saved full valuation measures to: {full_csv}")

    # Build and save 'Current' consolidated table (wide format) - only latest date
    # Filter to only the most recent date in the full dataset
    latest_date = full_df['Fetch_Date'].max()
    latest_data = full_df[full_df['Fetch_Date'] == latest_date].copy()
    
    # Create wide format for current data
    current_df = latest_data.pivot_table(
        index=["Ticker", "Data_Source"], 
        columns="Measure", 
        values="Value_Formatted",
        aggfunc='first'  # Take first value if duplicates exist
    ).reset_index()
    
    # Add Fetch_Date column at the beginning
    current_df.insert(0, 'Fetch_Date', latest_date)

    current_csv = os.path.join(csv_dir, "valuation_measures_current.csv")
    current_df.to_csv(current_csv, index=False)
    print(f"[2] Saved consolidated 'Current' table to: {current_csv}")
    print(f"    Format: Latest date ({latest_date}) - Each ticker has 2 rows (yahoo_finance + stockanalysis)")


    if failed:
        print("\nTickers failed:")
        for t in failed:
            print("  -", t)


if __name__ == "__main__":
    crawl_magnificent7()
