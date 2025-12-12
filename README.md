# web-crawling-financial-data

- A Python-based financial data crawler and visualization tool for analyzing valuation metrics of the Magnificent 7 tech stocks (AAPL, AMZN, GOOG, META, MSFT, NVDA, TSLA).

- Leverage vibe coding with GitHub (Copilot Claude Sonnet 4.5)

## Overview

This project automatically fetches valuation data from multiple sources (Yahoo Finance and StockAnalysis.com), consolidates the metrics using standardized terminology, and generates comprehensive visualizations for comparative analysis.

## Key Features

- **Multi-Source Data Collection**: Fetches data from Yahoo Finance (API) and StockAnalysis.com (web scraping)
- **Term Consolidation**: Standardizes metric names across different data sources using a conversion table
- **Automated Visualizations**: Generates 6 types of PNG visualizations with consistent color coding
- **Dual Versions**: Creates both full datasets (7 companies) and filtered versions (excluding TSLA for better scale)
- **Mean Calculations**: Provides average values across both data sources for consensus metrics

## Data Sources

1. **Yahoo Finance** (via yfinance API)
   - Trailing P/E, Forward P/E, PEG Ratio, P/S Ratio, P/B Ratio
   - Market Cap, Enterprise Value, EV/EBITDA, EV/Revenue
   
2. **StockAnalysis.com** (via Selenium)
   - PE Ratio, Forward PE, PEG Ratio, PS Ratio, PB Ratio

## Metrics Tracked

- **Trailing P/E**: Historical price-to-earnings ratio
- **Forward P/E**: Expected price-to-earnings ratio
- **PEG Ratio**: P/E adjusted for growth rate
- **P/S Ratio**: Price-to-sales ratio
- **P/B Ratio**: Price-to-book ratio
- **VCR**: Valuation Compression Ratio (Forward P/E / Trailing P/E)
- Enterprise Value, Market Cap, EV/EBITDA, EV/Revenue

## Generated Visualizations

1. **Yahoo Finance v1/v2**: Comprehensive 10-chart dashboard with heatmap
2. **Consolidated v1/v2**: Side-by-side comparison of both data sources (6 metrics)
3. **Consolidated Mean v1/v2**: Average values from both sources (6 metrics)

Each visualization includes date stamps and data source attribution.

## Project Structure

```
├── s00_term_conversion_table.csv   # Metric name standardization mapping
├── s01_fetch_data.py                # Data collection script
├── s02_visualize.py                 # Visualization generation
├── csv/                             # Output data files
│   ├── valuation_measures_full.csv
│   └── valuation_measures_current.csv
├── pic/                             # Generated visualizations
└── test/                            # Testing and utility scripts
```

## Usage

1. **Fetch Data**:
   ```bash
   python s01_fetch_data.py
   ```
   Generates CSV files with timestamped valuation data.

2. **Create Visualizations**:
   ```bash
   python s02_visualize.py
   ```
   Generates 6 PNG files with comprehensive charts.

## Requirements

- Python 3.12+
- yfinance 0.2.66
- selenium 4.39.0
- pandas 2.3.1
- matplotlib 3.8.2
- seaborn 0.13.2
- Chrome WebDriver (for Selenium)

## Installation

```bash
pip install -r requirements.txt
```

## Output Files

### CSV Files
- `valuation_measures_full.csv`: Tidy format with all data points
- `valuation_measures_current.csv`: Wide format for easy comparison

### PNG Files
- Yahoo Finance visualizations (v1, v2)
- Consolidated comparison charts (v1, v2)
- Consolidated mean charts (v1, v2)

## Features

✅ Automated data collection from multiple sources  
✅ Consistent color coding per company across all charts  
✅ Duplicate fetch prevention (checks existing data)  
✅ Graceful error handling for failed requests  
✅ Rate limiting for polite web scraping  
✅ Consolidated terminology across data sources  

## Notes

- **v1 files**: Include all 7 companies
- **v2 files**: Exclude TSLA for better scale visualization
- Data is fetched with date stamps for historical tracking
- StockAnalysis.com scraping runs in headless Chrome mode