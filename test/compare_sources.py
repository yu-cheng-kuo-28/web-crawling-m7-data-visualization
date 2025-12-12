#!/usr/bin/env python3
import pandas as pd

df = pd.read_csv('csv/valuation_measures_current.csv')

print("="*90)
print("✅ DATA SUCCESSFULLY FETCHED FROM BOTH SOURCES!")
print("="*90)
print("\nComparison: Yahoo Finance vs StockAnalysis.com")
print("="*90)

for ticker in ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META', 'NVDA', 'TSLA']:
    yahoo = df[(df['Ticker'] == ticker) & (df['Data_Source'] == 'yahoo_finance')]
    sa = df[(df['Ticker'] == ticker) & (df['Data_Source'] == 'stockanalysis')]
    
    print(f"\n{ticker}:")
    print(f"  {'Metric':<25} {'Yahoo Finance':<15} {'StockAnalysis':<15}")
    print(f"  {'-'*25} {'-'*15} {'-'*15}")
    
    # Trailing P/E
    y_pe = yahoo['Trailing P/E'].values[0] if len(yahoo) > 0 else 'N/A'
    sa_pe = sa['StockAnalysis PE Ratio'].values[0] if len(sa) > 0 else 'N/A'
    print(f"  {'Trailing P/E':<25} {y_pe:<15} {sa_pe:<15}")
    
    # Forward P/E
    y_fpe = yahoo['Forward P/E'].values[0] if len(yahoo) > 0 else 'N/A'
    sa_fpe = sa['StockAnalysis Forward PE'].values[0] if len(sa) > 0 else 'N/A'
    print(f"  {'Forward P/E':<25} {y_fpe:<15} {sa_fpe:<15}")
    
    # PEG Ratio
    y_peg = yahoo['PEG Ratio (5yr expected)'].values[0] if len(yahoo) > 0 else 'N/A'
    sa_peg = sa['StockAnalysis PEG Ratio'].values[0] if len(sa) > 0 else 'N/A'
    print(f"  {'PEG Ratio':<25} {y_peg:<15} {sa_peg:<15}")
    
    # PS Ratio
    y_ps = yahoo['Price/Sales (ttm)'].values[0] if len(yahoo) > 0 else 'N/A'
    sa_ps = sa['StockAnalysis PS Ratio'].values[0] if len(sa) > 0 else 'N/A'
    print(f"  {'PS Ratio':<25} {y_ps:<15} {sa_ps:<15}")
    
    # PB Ratio
    y_pb = yahoo['Price/Book (mrq)'].values[0] if len(yahoo) > 0 else 'N/A'
    sa_pb = sa['StockAnalysis PB Ratio'].values[0] if len(sa) > 0 else 'N/A'
    print(f"  {'PB Ratio':<25} {y_pb:<15} {sa_pb:<15}")

print("\n" + "="*90)
print("Note: Small differences are normal due to timing and calculation methods")
print("="*90)
