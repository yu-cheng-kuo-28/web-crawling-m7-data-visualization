#!/usr/bin/env python3
import pandas as pd

df = pd.read_csv('csv/valuation_measures_current.csv')

print("="*70)
print("✅ NASDAQ DATA SUCCESSFULLY FETCHED!")
print("="*70)
print("\nData Comparison - Yahoo Finance vs NASDAQ:")
print("="*70)

for ticker in ['GOOG', 'AMZN', 'META', 'TSLA']:
    yahoo = df[(df['Ticker'] == ticker) & (df['Data_Source'] == 'yahoo_finance')]
    nasdaq = df[(df['Ticker'] == ticker) & (df['Data_Source'] == 'nasdaq')]
    
    print(f"\n{ticker}:")
    print(f"  Yahoo PEG (5yr):        {yahoo['PEG Ratio (5yr expected)'].values[0]}")
    print(f"  NASDAQ PEG (12-month):  {nasdaq['NASDAQ PEG Ratio'].values[0]}")
    print(f"  Yahoo Forward P/E:      {yahoo['Forward P/E'].values[0]}")
    print(f"  NASDAQ 2025 P/E Est:    {nasdaq['NASDAQ P/E 2025 Estimate'].values[0]}")
    print(f"  NASDAQ 2024 P/E Actual: {nasdaq['NASDAQ P/E 2024 Actual'].values[0]}")

print("\n" + "="*70)
print("⚠️  NOTE: AAPL, MSFT, NVDA - Page loading issues (retry recommended)")
print("="*70)
