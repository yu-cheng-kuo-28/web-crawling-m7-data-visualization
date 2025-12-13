# Configuration Guide

## Overview

The project uses two separate configuration files:
- **config/01_config_fetch.yaml** - Controls which stocks to fetch in `s01_fetch_data.py`
- **config/02_config_visualize.yaml** - Controls visualization settings in `s02_visualize.py`

This separation allows you to fetch data for many stocks while only visualizing a subset.

## config/01_config_fetch.yaml - Data Fetching Configuration

Controls which stocks to fetch data for:

### Structure

```yaml
# List of stock tickers to fetch data for
tickers:
  - AAPL
  - MSFT
  - GOOG
  # ... add more tickers here

# Tickers to exclude from filtered visualizations (v2 versions)
exclude_from_visualizations:
  - TSLA

# Visualization settings
visualization:
  create_filtered_version: true  # Create v2 versions excluding certain tickers
  filtered_version_label: "w/o TSLA"  # Label for filtered versions
```

### How to Use

#### 1. **Adding New Stocks**

Edit `config/01_config_fetch.yaml` and add ticker symbols to the `tickers` list:

```yaml
tickers:
  # Magnificent 7
  - AAPL
  - MSFT
  - GOOG
  - AMZN
  - META
  - NVDA
  - TSLA
  
  # Additional stocks
  - NFLX
  - AMD
  - INTC
```

#### 2. **Fetching Data**

Run the fetch script:
```bash
python s01_fetch_data.py
```

The script will:
- Load tickers from `config/01_config_fetch.yaml`
- Fetch data from Yahoo Finance and StockAnalysis.com
- Save to `csv/valuation_measures_full.csv` and `csv/valuation_measures_current.csv`

#### 3. **Creating Visualizations**

Run the visualization script:
```bash
python s02_visualize.py
```

The script will:
- Read all available stock data from CSV files
- Create visualizations for all stocks
- If `create_filtered_version: true`, create v2 versions excluding stocks listed in `exclude_from_visualizations`

### Visualization Options

#### Create Full and Filtered Versions
```yaml
visualization:
  create_filtered_version: true
  filtered_version_label: "w/o TSLA"

exclude_from_visualizations:
  - TSLA
```

This creates:
- **v1 files**: All stocks
- **v2 files**: Excluding TSLA (for better scale when one stock has extreme values)

#### Create Only Full Versions
```yaml
visualization:
  create_filtered_version: false
```

This creates only v1 files with all stocks.

#### Exclude Multiple Stocks
```yaml
exclude_from_visualizations:
  - TSLA
  - NFLX
  - AMD
  
visualization:
  filtered_version_label: "Top 4"
```

### Examples

#### Example 1: Fetch FAANG Stocks
```yaml
tickers:
  - META  # Facebook
  - AAPL  # Apple
  - AMZN  # Amazon
  - NFLX  # Netflix
  - GOOG  # Google

exclude_from_visualizations: []

visualization:
  create_filtered_version: false
```

#### Example 2: Tech Giants with Filtered View
```yaml
tickers:
  - AAPL
  - MSFT
  - GOOG
  - AMZN
  - META
  - NVDA
  - TSLA
  - NFLX
  - AMD
  - INTC

exclude_from_visualizations:
  - TSLA
  - INTC

visualization:
  create_filtered_version: true
  filtered_version_label: "Top 8"
```

#### Example 3: Semiconductor Stocks
```yaml
tickers:
  - NVDA
  - AMD
  - INTC
  - QCOM
  - AVGO
  - TXN

exclude_from_visualizations: []

visualization:
  create_filtered_version: false
```

### Output Files

After running both scripts, you'll find:

**Data Files** (`csv/` folder):
- `valuation_measures_full.csv` - Historical data (all dates, tidy format)
- `valuation_measures_current.csv` - Latest data only (wide format)

**Visualization Files** (`pic/YYYY_MMDD/` folder):
- `yahoo_finance_v1.png` - All stocks
- `yahoo_finance_v2.png` - Filtered stocks (if enabled)
- `consolidated_separated_v1.png` - Comparison of both data sources, all stocks
- `consolidated_separated_v2.png` - Comparison, filtered stocks (if enabled)
- `consolidated_mean_v1.png` - Average of both sources, all stocks
- `consolidated_mean_v2.png` - Average, filtered stocks (if enabled)

### Tips

1. **Data Quality**: Not all stocks have complete data on StockAnalysis.com. Check the console output for any failures.

2. **Chart Readability**: If you have many stocks with widely different valuations, use `exclude_from_visualizations` to create cleaner v2 charts.

3. **Historical Data**: The fetch script appends new data instead of overwriting. To re-fetch, delete the specific date rows from `valuation_measures_full.csv`.

4. **Backup**: The default config includes Magnificent 7 stocks as a fallback if `config/01_config_fetch.yaml` is missing or invalid.
