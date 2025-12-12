#!/bin/bash
# Pipeline to fetch Yahoo Finance data and create visualizations
# This script runs the complete data collection and visualization workflow

echo "=========================================="
echo "Yahoo Finance Data Pipeline"
echo "=========================================="
echo ""

# Determine Python command (python or python3)
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "Error: Python not found. Please install Python."
    exit 1
fi

# Step 1: Fetch data from Yahoo Finance
echo "Step 1: Fetching valuation data from Yahoo Finance..."
$PYTHON_CMD ./s01_fetch_data.py

# Check if the previous command was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to fetch data from Yahoo Finance"
    exit 1
fi

echo ""
echo "Step 2: Creating visualizations..."
$PYTHON_CMD ./s02_visualize.py

# Check if the previous command was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to create visualizations"
    exit 1
fi

echo ""
echo "=========================================="
echo "Pipeline completed successfully!"
echo "=========================================="
echo "- CSV files saved in ./csv/"
echo "- Visualizations saved in ./pic/"
