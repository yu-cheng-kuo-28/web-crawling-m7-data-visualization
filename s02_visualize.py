#!/usr/bin/env python3
"""
Visualize Yahoo Finance Valuation Measures for the Magnificent 7
Creates multiple charts to compare valuation metrics across companies.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10


def parse_value(val):
    """Convert formatted values like '4.14T', '37.32' back to numbers"""
    if pd.isna(val) or val == 'N/A':
        return np.nan
    
    val = str(val).strip()
    if val.endswith('T'):
        return float(val[:-1]) * 1_000_000_000_000
    elif val.endswith('B'):
        return float(val[:-1]) * 1_000_000_000
    elif val.endswith('M'):
        return float(val[:-1]) * 1_000_000
    else:
        try:
            return float(val)
        except ValueError:
            return np.nan


def load_and_prepare_data(csv_file='csv/valuation_measures_current.csv', data_source='yahoo_finance'):
    """Load the CSV and prepare data for visualization
    
    Args:
        csv_file: Path to the CSV file
        data_source: Which data source to use ('yahoo_finance', 'stockanalysis', or 'both')
    """
    df = pd.read_csv(csv_file)
    
    # Filter by data source (default to yahoo_finance for visualization)
    if data_source != 'both':
        df = df[df['Data_Source'] == data_source].copy()
    
    # Parse numeric columns - using consolidated term names
    numeric_cols = ['Enterprise Value', 'Market Cap', 'Enterprise Value/EBITDA', 
                    'Enterprise Value/Revenue', 'Forward P/E', 'P/B Ratio', 
                    'P/S Ratio', 'Trailing P/E', 'PEG Ratio']
    
    for col in numeric_cols:
        if col in df.columns:
            df[f'{col}_numeric'] = df[col].apply(parse_value)
    
    # Calculate VCR (Valuation Compression Ratio) = Forward P/E / Trailing P/E
    # VCR < 1 means market expects earnings growth (forward earnings higher than trailing)
    # VCR > 1 means market expects earnings decline
    df['VCR_numeric'] = df['Forward P/E_numeric'] / df['Trailing P/E_numeric']
    df['VCR'] = df['VCR_numeric'].apply(lambda x: f"{x:.3f}" if not pd.isna(x) else "N/A")
    
    return df


def create_visualizations(df, version_suffix=''):
    """Create comprehensive visualizations"""
    
    # Create a figure with multiple subplots (4 rows x 3 columns for VCR chart)
    fig = plt.figure(figsize=(16, 16))
    
    # Get the fetch date and data source from the data
    fetch_date = df['Fetch_Date'].iloc[0] if 'Fetch_Date' in df.columns else datetime.now().strftime('%Y-%m-%d')
    data_source = df['Data_Source'].iloc[0] if 'Data_Source' in df.columns else 'yahoo_finance'
    
    # Determine title based on companies included
    company_list = ', '.join(sorted(df['Ticker'].tolist()))
    if len(df) < 7:
        title = f'Valuation Measures Comparison\nMagnificent 6 (w/o TSLA)\n(Data: {fetch_date}, Source: {data_source})'
    else:
        title = f'Valuation Measures Comparison\nMagnificent 7\n(Data: {fetch_date}, Source: {data_source})'
    
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.995)
    
    # Define consistent color mapping for each company (sub-figures 2-9) using Tableau 10 colors
    # Sort tickers to ensure consistent color assignment
    all_tickers = sorted(df['Ticker'].unique())
    tableau_colors = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F', '#BAB0AC']
    ticker_colors = {ticker: tableau_colors[i % len(tableau_colors)] for i, ticker in enumerate(all_tickers)}
    
    # TOP 1: P/E Ratios Comparison (Position 1 - Top Left)
    ax1 = plt.subplot(4, 3, 1)
    x = np.arange(len(df))
    width = 0.35
    trailing_pe = df.sort_values('Ticker')['Trailing P/E_numeric']
    forward_pe = df.sort_values('Ticker')['Forward P/E_numeric']
    tickers = df.sort_values('Ticker')['Ticker']
    
    ax1.bar(x - width/2, trailing_pe, width, label='Trailing P/E', alpha=0.8)
    ax1.bar(x + width/2, forward_pe, width, label='Forward P/E', alpha=0.8)
    ax1.set_ylabel('P/E Ratio')
    ax1.set_title('P/E Ratios: Trailing vs Forward', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(tickers, rotation=45)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # TOP 2: VCR - Valuation Compression Ratio (Position 2 - Top Center)
    ax2 = plt.subplot(4, 3, 2)
    vcr_sorted = df.sort_values('VCR_numeric', ascending=True).dropna(subset=['VCR_numeric'])
    
    # Use consistent colors for each company - lollipop chart
    bar_colors = [ticker_colors[ticker] for ticker in vcr_sorted['Ticker']]
    y_pos = np.arange(len(vcr_sorted))
    ax2.hlines(y=y_pos, xmin=0, xmax=vcr_sorted['VCR_numeric'], color='gray', alpha=0.4, linewidth=1)
    ax2.scatter(vcr_sorted['VCR_numeric'], y_pos, color=bar_colors, s=200, alpha=0.85, edgecolors='black', linewidth=1.5)
    
    ax2.set_xlabel('VCR Ratio (Forward P/E / Trailing P/E)', fontsize=10)
    ax2.set_title('VCR - Valuation Compression Ratio\n<1: Growth | >1: Decline', 
                  fontweight='bold', fontsize=11)
    ax2.axvline(x=1.0, color='#E15759', linestyle='--', linewidth=2, label='VCR=1.0')
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(vcr_sorted['Ticker'], fontsize=10)
    ax2.grid(axis='x', alpha=0.4, linestyle='--', linewidth=0.5)
    ax2.legend(loc='best', fontsize=9)
    
    # Dynamic offset: 4% of data range + minimum offset
    vcr_range = vcr_sorted['VCR_numeric'].max() - vcr_sorted['VCR_numeric'].min()
    vcr_offset = max(vcr_range * 0.04, 0.02)
    for i, (idx, row) in enumerate(vcr_sorted.iterrows()):
        ax2.text(row['VCR_numeric'] + vcr_offset, i, 
                f"{row['VCR_numeric']:.3f}", 
                va='center', ha='left', fontsize=9, fontweight='bold')
    
    # TOP 3: PEG Ratio (Position 3 - Top Right)
    ax3 = plt.subplot(4, 3, 3)
    peg_sorted = df.sort_values('PEG Ratio_numeric', ascending=True).dropna(subset=['PEG Ratio_numeric'])
    bar_colors = [ticker_colors[ticker] for ticker in peg_sorted['Ticker']]
    y_pos = np.arange(len(peg_sorted))
    ax3.hlines(y=y_pos, xmin=0, xmax=peg_sorted['PEG Ratio_numeric'], color='gray', alpha=0.4, linewidth=1)
    ax3.scatter(peg_sorted['PEG Ratio_numeric'], y_pos, color=bar_colors, s=200, alpha=0.85, edgecolors='black', linewidth=1.5)
    ax3.set_xlabel('PEG Ratio', fontsize=10)
    ax3.set_title('PEG Ratio (5yr expected)\nLower = Better Value', fontweight='bold', fontsize=11)
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(peg_sorted['Ticker'], fontsize=10)
    ax3.grid(axis='x', alpha=0.4, linestyle='--', linewidth=0.5)
    
    # Dynamic offset: 4% of data range + minimum offset
    peg_range = peg_sorted['PEG Ratio_numeric'].max() - peg_sorted['PEG Ratio_numeric'].min()
    peg_offset = max(peg_range * 0.04, 0.2)
    for i, (idx, row) in enumerate(peg_sorted.iterrows()):
        ax3.text(row['PEG Ratio_numeric'] + peg_offset, i, 
                f"{row['PEG Ratio_numeric']:.2f}", 
                va='center', ha='left', fontsize=9, fontweight='bold')
    
    # 4. Market Cap Comparison (Position 4 - Row 2 Left)
    ax4 = plt.subplot(4, 3, 4)
    market_caps = df.sort_values('Market Cap_numeric', ascending=True)
    bar_colors = [ticker_colors[ticker] for ticker in market_caps['Ticker']]
    y_pos = np.arange(len(market_caps))
    ax4.hlines(y=y_pos, xmin=0, xmax=market_caps['Market Cap_numeric'] / 1e12, color='gray', alpha=0.4, linewidth=1)
    ax4.scatter(market_caps['Market Cap_numeric'] / 1e12, y_pos, color=bar_colors, s=200, alpha=0.85, edgecolors='black', linewidth=1.5)
    ax4.set_xlabel('Market Cap (Trillions $)', fontsize=10)
    ax4.set_title('Market Capitalization', fontweight='bold', fontsize=11)
    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(market_caps['Ticker'], fontsize=10)
    ax4.grid(axis='x', alpha=0.4, linestyle='--', linewidth=0.5)
    
    # Dynamic offset: 4% of data range + minimum offset
    mc_range = (market_caps['Market Cap_numeric'].max() - market_caps['Market Cap_numeric'].min()) / 1e12
    mc_offset = max(mc_range * 0.04, 0.06)
    for i, (idx, row) in enumerate(market_caps.iterrows()):
        ax4.text(row['Market Cap_numeric'] / 1e12 + mc_offset, i, 
                f"${row['Market Cap_numeric']/1e12:.2f}T", 
                va='center', ha='left', fontsize=9, fontweight='bold')
    
    # 5. Enterprise Value Comparison (Position 5 - Row 2 Center)
    ax5 = plt.subplot(4, 3, 5)
    ev_sorted = df.sort_values('Enterprise Value_numeric', ascending=True)
    bar_colors = [ticker_colors[ticker] for ticker in ev_sorted['Ticker']]
    y_pos = np.arange(len(ev_sorted))
    ax5.hlines(y=y_pos, xmin=0, xmax=ev_sorted['Enterprise Value_numeric'] / 1e12, color='gray', alpha=0.4, linewidth=1)
    ax5.scatter(ev_sorted['Enterprise Value_numeric'] / 1e12, y_pos, color=bar_colors, s=200, alpha=0.85, edgecolors='black', linewidth=1.5)
    ax5.set_xlabel('Enterprise Value (Trillions $)', fontsize=10)
    ax5.set_title('Enterprise Value', fontweight='bold', fontsize=11)
    ax5.set_yticks(y_pos)
    ax5.set_yticklabels(ev_sorted['Ticker'], fontsize=10)
    ax5.grid(axis='x', alpha=0.4, linestyle='--', linewidth=0.5)
    
    # Dynamic offset: 4% of data range + minimum offset
    ev_range = (ev_sorted['Enterprise Value_numeric'].max() - ev_sorted['Enterprise Value_numeric'].min()) / 1e12
    ev_offset = max(ev_range * 0.04, 0.06)
    for i, (idx, row) in enumerate(ev_sorted.iterrows()):
        ax5.text(row['Enterprise Value_numeric'] / 1e12 + ev_offset, i, 
                f"${row['Enterprise Value_numeric']/1e12:.2f}T", 
                va='center', ha='left', fontsize=9, fontweight='bold')
    
    # 6. Price/Sales (Position 6 - Row 2 Right)
    ax6 = plt.subplot(4, 3, 6)
    ps_sorted = df.sort_values('P/S Ratio_numeric', ascending=True)
    bar_colors = [ticker_colors[ticker] for ticker in ps_sorted['Ticker']]
    y_pos = np.arange(len(ps_sorted))
    ax6.hlines(y=y_pos, xmin=0, xmax=ps_sorted['P/S Ratio_numeric'], color='gray', alpha=0.4, linewidth=1)
    ax6.scatter(ps_sorted['P/S Ratio_numeric'], y_pos, color=bar_colors, s=200, alpha=0.85, edgecolors='black', linewidth=1.5)
    ax6.set_xlabel('Price/Sales Ratio', fontsize=10)
    ax6.set_title('Price/Sales (TTM)', fontweight='bold', fontsize=11)
    ax6.set_yticks(y_pos)
    ax6.set_yticklabels(ps_sorted['Ticker'], fontsize=10)
    ax6.grid(axis='x', alpha=0.4, linestyle='--', linewidth=0.5)
    
    # Dynamic offset: 4% of data range + minimum offset
    ps_range = ps_sorted['P/S Ratio_numeric'].max() - ps_sorted['P/S Ratio_numeric'].min()
    ps_offset = max(ps_range * 0.04, 0.3)
    for i, (idx, row) in enumerate(ps_sorted.iterrows()):
        ax6.text(row['P/S Ratio_numeric'] + ps_offset, i, 
                f"{row['P/S Ratio_numeric']:.2f}", 
                va='center', ha='left', fontsize=9, fontweight='bold')
    
    # 7. Price/Book Ratio (Position 7 - Row 3 Left)
    ax7 = plt.subplot(4, 3, 7)
    pb_sorted = df.sort_values('P/B Ratio_numeric', ascending=True)
    bar_colors = [ticker_colors[ticker] for ticker in pb_sorted['Ticker']]
    y_pos = np.arange(len(pb_sorted))
    ax7.hlines(y=y_pos, xmin=0, xmax=pb_sorted['P/B Ratio_numeric'], color='gray', alpha=0.4, linewidth=1)
    ax7.scatter(pb_sorted['P/B Ratio_numeric'], y_pos, color=bar_colors, s=200, alpha=0.85, edgecolors='black', linewidth=1.5)
    ax7.set_xlabel('Price/Book Ratio', fontsize=10)
    ax7.set_title('Price/Book (MRQ)', fontweight='bold', fontsize=11)
    ax7.set_yticks(y_pos)
    ax7.set_yticklabels(pb_sorted['Ticker'], fontsize=10)
    ax7.grid(axis='x', alpha=0.4, linestyle='--', linewidth=0.5)
    
    # Dynamic offset: 4% of data range + minimum offset
    pb_range = pb_sorted['P/B Ratio_numeric'].max() - pb_sorted['P/B Ratio_numeric'].min()
    pb_offset = max(pb_range * 0.04, 1.0)
    for i, (idx, row) in enumerate(pb_sorted.iterrows()):
        ax7.text(row['P/B Ratio_numeric'] + pb_offset, i, 
                f"{row['P/B Ratio_numeric']:.2f}", 
                va='center', ha='left', fontsize=9, fontweight='bold')
    
    # 8. Enterprise Value/Revenue (Position 8 - Row 3 Center)
    ax8 = plt.subplot(4, 3, 8)
    evr_sorted = df.sort_values('Enterprise Value/Revenue_numeric', ascending=True)
    bar_colors = [ticker_colors[ticker] for ticker in evr_sorted['Ticker']]
    y_pos = np.arange(len(evr_sorted))
    ax8.hlines(y=y_pos, xmin=0, xmax=evr_sorted['Enterprise Value/Revenue_numeric'], color='gray', alpha=0.4, linewidth=1)
    ax8.scatter(evr_sorted['Enterprise Value/Revenue_numeric'], y_pos, color=bar_colors, s=200, alpha=0.85, edgecolors='black', linewidth=1.5)
    ax8.set_xlabel('EV/Revenue Ratio', fontsize=10)
    ax8.set_title('Enterprise Value / Revenue', fontweight='bold', fontsize=11)
    ax8.set_yticks(y_pos)
    ax8.set_yticklabels(evr_sorted['Ticker'], fontsize=10)
    ax8.grid(axis='x', alpha=0.4, linestyle='--', linewidth=0.5)
    
    # Dynamic offset: 4% of data range + minimum offset
    evr_range = evr_sorted['Enterprise Value/Revenue_numeric'].max() - evr_sorted['Enterprise Value/Revenue_numeric'].min()
    evr_offset = max(evr_range * 0.04, 0.3)
    for i, (idx, row) in enumerate(evr_sorted.iterrows()):
        ax8.text(row['Enterprise Value/Revenue_numeric'] + evr_offset, i, 
                f"{row['Enterprise Value/Revenue_numeric']:.2f}", 
                va='center', ha='left', fontsize=9, fontweight='bold')
    
    # 9. Enterprise Value/EBITDA (Position 9 - Row 3 Right)
    ax9 = plt.subplot(4, 3, 9)
    evebitda_sorted = df.sort_values('Enterprise Value/EBITDA_numeric', ascending=True)
    bar_colors = [ticker_colors[ticker] for ticker in evebitda_sorted['Ticker']]
    y_pos = np.arange(len(evebitda_sorted))
    ax9.hlines(y=y_pos, xmin=0, xmax=evebitda_sorted['Enterprise Value/EBITDA_numeric'], color='gray', alpha=0.4, linewidth=1)
    ax9.scatter(evebitda_sorted['Enterprise Value/EBITDA_numeric'], y_pos, color=bar_colors, s=200, alpha=0.85, edgecolors='black', linewidth=1.5)
    ax9.set_xlabel('EV/EBITDA Ratio', fontsize=10)
    ax9.set_title('Enterprise Value / EBITDA', fontweight='bold', fontsize=11)
    ax9.set_yticks(y_pos)
    ax9.set_yticklabels(evebitda_sorted['Ticker'], fontsize=10)
    ax9.grid(axis='x', alpha=0.4, linestyle='--', linewidth=0.5)
    
    # Dynamic offset: 4% of data range + minimum offset
    evebitda_range = evebitda_sorted['Enterprise Value/EBITDA_numeric'].max() - evebitda_sorted['Enterprise Value/EBITDA_numeric'].min()
    evebitda_offset = max(evebitda_range * 0.04, 2.0)
    for i, (idx, row) in enumerate(evebitda_sorted.iterrows()):
        ax9.text(row['Enterprise Value/EBITDA_numeric'] + evebitda_offset, i, 
                f"{row['Enterprise Value/EBITDA_numeric']:.2f}", 
                va='center', ha='left', fontsize=9, fontweight='bold')
    
    # 10. Valuation Multiples Heatmap (Bottom Row - spanning 3 columns)
    ax10 = plt.subplot(4, 3, (10, 12))
    
    # Create heatmap data including PEG Ratio
    heatmap_cols = ['Trailing P/E_numeric', 'Forward P/E_numeric', 'VCR_numeric', 'PEG Ratio_numeric',
                    'P/S Ratio_numeric', 'P/B Ratio_numeric',
                    'Enterprise Value/Revenue_numeric', 'Enterprise Value/EBITDA_numeric']
    heatmap_labels = ['Trailing P/E', 'Forward P/E', 'VCR', 'PEG', 'P/S', 'P/B', 'EV/Rev', 'EV/EBITDA']
    
    heatmap_data = df.set_index('Ticker')[heatmap_cols].copy()
    heatmap_data.columns = heatmap_labels
    
    # Normalize each column for better visualization (0-1 scale)
    heatmap_normalized = (heatmap_data - heatmap_data.min()) / (heatmap_data.max() - heatmap_data.min())
    
    sns.heatmap(heatmap_normalized.T, annot=heatmap_data.T, fmt='.2f', 
                cmap='RdYlGn_r', cbar_kws={'label': 'Relative Valuation'}, 
                ax=ax10, linewidths=0.5)
    ax10.set_title('Valuation Multiples Heatmap (Lower = Better Value)', fontweight='bold')
    ax10.set_xlabel('')
    ax10.set_ylabel('Metric')
    
    plt.tight_layout()
    
    # Create pic directory with date-specific subdirectory
    timestamp = datetime.now().strftime('%Y_%m%d')
    pic_dir = os.path.join('pic', timestamp)
    os.makedirs(pic_dir, exist_ok=True)
    
    # Generate filename with data source
    data_source = df['Data_Source'].iloc[0] if 'Data_Source' in df.columns else 'yahoo_finance'
    
    # Add version suffix if filtered
    if len(df) < 7:
        excluded = list(set(['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META', 'NVDA', 'TSLA']) - set(df['Ticker'].tolist()))
        suffix = '_v2'
        #! Commented out this
        # suffix = f"_v2_no_{'_'.join(excluded)}"
    else:
        suffix = '_v1'
    
    output_file = os.path.join(pic_dir, f'{data_source}{suffix}.png')
    
    # Save the figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved comprehensive visualization to: {output_file}")
    
    return fig


def create_consolidated_visualizations(df_full, version='v1'):
    """Create consolidated visualizations comparing Yahoo Finance vs StockAnalysis
    
    Args:
        df_full: Full dataframe with both data sources
        version: 'v1' for all companies, 'v2' for filtered (no TSLA)
    """
    # Filter data for both sources
    df_yahoo = df_full[df_full['Data_Source'] == 'yahoo_finance'].copy()
    df_sa = df_full[df_full['Data_Source'] == 'stockanalysis'].copy()
    
    # Merge on Ticker to get side-by-side comparison
    df_merged = pd.merge(df_yahoo, df_sa, on='Ticker', suffixes=('_yahoo', '_sa'))
    
    # Create figure with 6 subplots (2x3)
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    
    # Get fetch date from the data
    fetch_date = df_full['Fetch_Date'].iloc[0] if 'Fetch_Date' in df_full.columns else datetime.now().strftime('%Y-%m-%d')
    
    # Determine title based on version
    if version == 'v2':
        title = f'Consolidated Valuation Comparison\nYahoo Finance vs StockAnalysis\nMagnificent 6 (w/o TSLA)\n(Data: {fetch_date}, Sources: yahoo_finance + stockanalysis)'
    else:
        title = f'Consolidated Valuation Comparison\nYahoo Finance vs StockAnalysis\nMagnificent 7\n(Data: {fetch_date}, Sources: yahoo_finance + stockanalysis)'
    
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    # Define the 6 metrics to visualize (in display order)
    metrics = [
        ('Trailing P/E', 'Trailing P/E_numeric'),   # Fig 01
        ('Forward P/E', 'Forward P/E_numeric'),     # Fig 02
        ('VCR', 'VCR_numeric'),                     # Fig 03
        ('PEG Ratio', 'PEG Ratio_numeric'),         # Fig 04
        ('P/S Ratio', 'P/S Ratio_numeric'),         # Fig 05
        ('P/B Ratio', 'P/B Ratio_numeric')          # Fig 06
    ]
    
    # Color scheme - Tableau colors
    colors_yahoo = '#4E79A7'  # Tableau Blue
    colors_sa = '#F28E2B'     # Tableau Orange
    
    for idx, (title, col_base) in enumerate(metrics):
        ax = axes[idx // 3, idx % 3]
        
        col_yahoo = col_base + '_yahoo'
        col_sa = col_base + '_sa'
        
        # Sort by Yahoo Finance values
        df_plot = df_merged.sort_values(col_yahoo, ascending=True).dropna(subset=[col_yahoo])
        
        x = np.arange(len(df_plot))
        width = 0.35
        
        # Plot bars with improved styling
        bars1 = ax.barh(x - width/2, df_plot[col_yahoo], width, 
                        label='Yahoo Finance', color=colors_yahoo, alpha=0.85, edgecolor='black', linewidth=0.5)
        bars2 = ax.barh(x + width/2, df_plot[col_sa], width, 
                        label='StockAnalysis', color=colors_sa, alpha=0.85, edgecolor='black', linewidth=0.5)
        
        ax.set_xlabel(title, fontsize=10)
        ax.set_title(f'{title} Comparison', fontweight='bold', fontsize=11)
        ax.set_yticks(x)
        ax.set_yticklabels(df_plot['Ticker'], fontsize=10)
        ax.legend(loc='best', fontsize=9)
        ax.grid(axis='x', alpha=0.4, linestyle='--', linewidth=0.5)
        
        # Calculate dynamic offset based on data range
        combined_values = pd.concat([df_plot[col_yahoo], df_plot[col_sa]]).dropna()
        data_range = combined_values.max() - combined_values.min()
        # Set appropriate minimum offset for each metric
        if title == 'VCR':
            min_offset = 0.015
        elif title == 'Trailing P/E' or title == 'Forward P/E':
            min_offset = 1.5
        elif title == 'PEG Ratio':
            min_offset = 0.15
        elif title == 'P/S Ratio':
            min_offset = 0.3
        else:  # P/B Ratio
            min_offset = 0.8
        offset = max(data_range * 0.025, min_offset)
        
        # Add value labels (adjust format for VCR which uses 3 decimals)
        for i, (_, row) in enumerate(df_plot.iterrows()):
            if not pd.isna(row[col_yahoo]):
                if title == 'VCR':
                    label_text = f"{row[col_yahoo]:.3f}"
                else:
                    label_text = f"{row[col_yahoo]:.2f}"
                ax.text(row[col_yahoo] + offset, i - width/2, label_text, 
                       va='center', ha='left', fontsize=8, color=colors_yahoo)
            if not pd.isna(row[col_sa]):
                if title == 'VCR':
                    label_text = f"{row[col_sa]:.3f}"
                else:
                    label_text = f"{row[col_sa]:.2f}"
                ax.text(row[col_sa] + offset, i + width/2, label_text, 
                       va='center', ha='left', fontsize=8, color=colors_sa)
    
    plt.tight_layout()
    
    # Create pic directory with date-specific subdirectory
    timestamp = datetime.now().strftime('%Y_%m%d')
    pic_dir = os.path.join('pic', timestamp)
    os.makedirs(pic_dir, exist_ok=True)
    
    # Generate filename
    output_file = os.path.join(pic_dir, f'consolidated_separated_{version}.png')
    
    # Save the figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved consolidated visualization to: {output_file}")
    
    return fig


def create_consolidated_mean_visualizations(df_full, version='v1'):
    """Create consolidated mean visualizations showing average of both sources
    
    Args:
        df_full: Full dataframe with both data sources
        version: 'v1' for all companies, 'v2' for filtered (no TSLA)
    """
    # Filter data for both sources
    df_yahoo = df_full[df_full['Data_Source'] == 'yahoo_finance'].copy()
    df_sa = df_full[df_full['Data_Source'] == 'stockanalysis'].copy()
    
    # Merge on Ticker to get side-by-side comparison
    df_merged = pd.merge(df_yahoo, df_sa, on='Ticker', suffixes=('_yahoo', '_sa'))
    
    # Get fetch date from the data
    fetch_date = df_full['Fetch_Date'].iloc[0] if 'Fetch_Date' in df_full.columns else datetime.now().strftime('%Y-%m-%d')
    
    # Create consistent color mapping for each company using Tableau 10 colors
    all_tickers = sorted(df_merged['Ticker'].unique())
    tableau_colors = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F', '#BAB0AC']
    ticker_colors = {ticker: tableau_colors[i % len(tableau_colors)] for i, ticker in enumerate(all_tickers)}
    
    # Create figure with 6 subplots (2x3)
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    
    # Determine title based on version
    if version == 'v2':
        title = f'Consolidated Mean Valuation\nAverage of Yahoo Finance & StockAnalysis\nMagnificent 6 (w/o TSLA)\n(Data: {fetch_date}, Sources: yahoo_finance + stockanalysis)'
    else:
        title = f'Consolidated Mean Valuation\nAverage of Yahoo Finance & StockAnalysis\nMagnificent 7\n(Data: {fetch_date}, Sources: yahoo_finance + stockanalysis)'
    
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    # Define the 6 metrics to visualize (in display order)
    metrics = [
        ('Trailing P/E', 'Trailing P/E_numeric'),   # Fig 01
        ('Forward P/E', 'Forward P/E_numeric'),     # Fig 02
        ('VCR', 'VCR_numeric'),                     # Fig 03
        ('PEG Ratio', 'PEG Ratio_numeric'),         # Fig 04
        ('P/S Ratio', 'P/S Ratio_numeric'),         # Fig 05
        ('P/B Ratio', 'P/B Ratio_numeric')          # Fig 06
    ]
    
    for idx, (title_text, col_base) in enumerate(metrics):
        ax = axes[idx // 3, idx % 3]
        
        col_yahoo = col_base + '_yahoo'
        col_sa = col_base + '_sa'
        
        # Calculate mean of both sources
        df_merged[f'{col_base}_mean'] = df_merged[[col_yahoo, col_sa]].mean(axis=1)
        
        # Sort by mean values
        df_plot = df_merged.sort_values(f'{col_base}_mean', ascending=True).dropna(subset=[f'{col_base}_mean'])
        
        x = np.arange(len(df_plot))
        
        # Get colors for each company
        bar_colors = [ticker_colors[ticker] for ticker in df_plot['Ticker']]
        
        # Plot lollipop chart
        y_pos = np.arange(len(df_plot))
        ax.hlines(y=y_pos, xmin=0, xmax=df_plot[f'{col_base}_mean'], color='gray', alpha=0.4, linewidth=1)
        ax.scatter(df_plot[f'{col_base}_mean'], y_pos, color=bar_colors, s=200, alpha=0.85, edgecolors='black', linewidth=1.5)
        
        ax.set_xlabel(f'{title_text} (Mean)', fontsize=10)
        ax.set_title(f'{title_text}', fontweight='bold', fontsize=11)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(df_plot['Ticker'], fontsize=10)
        ax.grid(axis='x', alpha=0.4, linestyle='--', linewidth=0.5)
        
        # Add value labels with dynamic offset based on metric
        mean_range = df_plot[f'{col_base}_mean'].max() - df_plot[f'{col_base}_mean'].min()
        # Set appropriate minimum offset for each metric
        if title_text == 'VCR':
            min_offset = 0.02
        elif title_text == 'Trailing P/E' or title_text == 'Forward P/E':
            min_offset = 1.0
        elif title_text == 'PEG Ratio':
            min_offset = 0.15
        elif title_text == 'P/S Ratio':
            min_offset = 0.3
        else:  # P/B Ratio
            min_offset = 0.8
        offset = max(mean_range * 0.04, min_offset)
        for i, (_, row) in enumerate(df_plot.iterrows()):
            if not pd.isna(row[f'{col_base}_mean']):
                if title_text == 'VCR':
                    label_text = f"{row[f'{col_base}_mean']:.3f}"
                else:
                    label_text = f"{row[f'{col_base}_mean']:.2f}"
                ax.text(row[f'{col_base}_mean'] + offset, i, label_text, 
                       va='center', ha='left', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    
    # Create pic directory with date-specific subdirectory
    timestamp = datetime.now().strftime('%Y_%m%d')
    pic_dir = os.path.join('pic', timestamp)
    os.makedirs(pic_dir, exist_ok=True)
    
    # Generate filename
    output_file = os.path.join(pic_dir, f'consolidated_mean_{version}.png')
    
    # Save the figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved consolidated mean visualization to: {output_file}")
    
    return fig


def create_summary_stats(df):
    """Print summary statistics"""
    print("\n" + "="*80)
    print("MAGNIFICENT 7 - VALUATION MEASURES SUMMARY")
    print("="*80)
    
    print("\n📊 MARKET CAPITALIZATION RANKINGS:")
    print("-" * 80)
    mc_sorted = df.sort_values('Market Cap_numeric', ascending=False)
    for idx, row in mc_sorted.iterrows():
        print(f"  {row['Ticker']:6s} - {row['Market Cap']}")
    
    print("\n💰 VALUATION MULTIPLES - HIGHEST TO LOWEST:")
    print("-" * 80)
    
    metrics = [
        ('Trailing P/E', 'Trailing P/E_numeric'),
        ('Forward P/E', 'Forward P/E_numeric'),
        ('VCR (Valuation Compression Ratio)', 'VCR_numeric'),
        ('PEG Ratio', 'PEG Ratio_numeric'),
        ('Price/Sales', 'P/S Ratio_numeric'),
        ('Price/Book', 'P/B Ratio_numeric'),
        ('EV/Revenue', 'Enterprise Value/Revenue_numeric'),
        ('EV/EBITDA', 'Enterprise Value/EBITDA_numeric')
    ]
    
    for label, col in metrics:
        sorted_df = df.sort_values(col, ascending=False).dropna(subset=[col])
        print(f"\n  {label}:")
        for idx, row in sorted_df.iterrows():
            val = row[col]
            print(f"    {row['Ticker']:6s} - {val:8.2f}")
    
    print("\n" + "="*80)


def main():
    """Main execution function"""
    print("="*80)
    print("VALUATION MEASURES VISUALIZATION")
    print("="*80)
    
    # Part 1: Yahoo Finance visualizations (v1 & v2)
    print("\n[1/6] Creating Yahoo Finance visualizations...")
    print("-"*80)
    df_yahoo = load_and_prepare_data(data_source='yahoo_finance')
    
    print(f"Loaded Yahoo Finance data for {len(df_yahoo)} companies: {', '.join(df_yahoo['Ticker'].tolist())}")
    
    print("\nCreating Yahoo Finance v1 (all 7 companies)...")
    fig1 = create_visualizations(df_yahoo)
    
    create_summary_stats(df_yahoo)
    
    print("\n✓ Yahoo Finance v1 complete!")
    
    # Create version without TSLA (filtered for better scale)
    print("\nCreating Yahoo Finance v2 (without TSLA for better scale)...")
    df_yahoo_filtered = df_yahoo[df_yahoo['Ticker'] != 'TSLA'].copy()
    print(f"Filtered data: {', '.join(df_yahoo_filtered['Ticker'].tolist())}")
    
    fig2 = create_visualizations(df_yahoo_filtered)
    
    print("\n✓ Yahoo Finance v2 (without TSLA) complete!")
    
    # Part 2: Consolidated visualizations
    print("\n" + "="*80)
    print("[2/6] Creating Consolidated visualizations (Yahoo + StockAnalysis)...")
    print("-"*80)
    
    df_full = load_and_prepare_data(data_source='both')
    print(f"Loaded data from both sources:")
    print(f"  - Yahoo Finance: {len(df_full[df_full['Data_Source']=='yahoo_finance'])} companies")
    print(f"  - StockAnalysis: {len(df_full[df_full['Data_Source']=='stockanalysis'])} companies")
    
    print("\nCreating Consolidated v1 (all 7 companies)...")
    fig3 = create_consolidated_visualizations(df_full, version='v1')
    
    print("\n✓ Consolidated v1 complete!")
    
    # Part 3: Consolidated v2 without TSLA
    print("\nCreating Consolidated v2 (without TSLA for better scale)...")
    df_full_filtered = df_full[df_full['Ticker'] != 'TSLA'].copy()
    print(f"Filtered data: {', '.join(sorted(df_full_filtered['Ticker'].unique()))}")
    
    fig4 = create_consolidated_visualizations(df_full_filtered, version='v2')
    
    print("\n✓ Consolidated v2 (without TSLA) complete!")
    
    # Part 3: Consolidated Mean visualizations
    print("\n" + "="*80)
    print("[3/6] Creating Consolidated Mean visualizations (Average of both sources)...")
    print("-"*80)
    
    print("\nCreating Consolidated Mean v1 (all 7 companies)...")
    fig5 = create_consolidated_mean_visualizations(df_full, version='v1')
    
    print("\n✓ Consolidated Mean v1 complete!")
    
    print("\nCreating Consolidated Mean v2 (without TSLA for better scale)...")
    fig6 = create_consolidated_mean_visualizations(df_full_filtered, version='v2')
    
    print("\n✓ Consolidated Mean v2 (without TSLA) complete!")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\n✓ All visualizations have been saved to the ./pic/ folder:")
    print("  1. Yahoo Finance v1 (all 7 companies)")
    print("  2. Yahoo Finance v2 (without TSLA)")
    print("  3. Consolidated v1 (6 key metrics from both sources - all 7 companies)")
    print("  4. Consolidated v2 (6 key metrics from both sources - without TSLA)")
    print("  5. Consolidated Mean v1 (average of both sources - all 7 companies)")
    print("  6. Consolidated Mean v2 (average of both sources - without TSLA)")
    print("\n📊 Consolidated metrics: Trailing P/E, Forward P/E, PEG Ratio, P/S Ratio, P/B Ratio, VCR")
    print("\nVisualization complete! 🎉")
    
    # Show the plot
    # plt.show()


if __name__ == "__main__":
    main()
