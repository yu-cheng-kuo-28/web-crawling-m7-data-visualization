# Test Files Directory

This directory contains testing and utility scripts used during development.

## Files

### Core Test Scripts

- **test_yahoo_finance_api.py** - Tests Yahoo Finance API data fetching using yfinance library
- **test_stockanalysis_selenium.py** - Tests StockAnalysis.com web scraping using Selenium
- **test_find_api.py** - Research script for exploring alternative data source APIs

### Comparison Utilities

- **compare_sources.py** - Compares valuation metrics between Yahoo Finance and StockAnalysis data sources
- **show_comparison.py** - Displays side-by-side comparison of data from different sources

## Notes

- These scripts are for development and debugging purposes only
- Main production scripts are in the root directory (s01_fetch_data.py, s02_visualize.py)
- NASDAQ testing files were removed as StockAnalysis proved to be a more reliable data source
