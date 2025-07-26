# Stock Chart Plotter - Project Brief

## Project Overview

A Python command-line application that plots interactive stock charts from CSV data with exchange-specific trading hours filtering using the lightweight-charts-python library.

## Core Requirements

- **Input**: CSV files containing OHLCV (Open, High, Low, Close, Volume) stock data
- **Exchange Integration**: Support for multiple stock exchanges using exchange_calendars library
- **Trading Hours Filtering**: Filter data to show only official trading hours for each exchange
- **Interactive Charts**: Display candlestick charts using lightweight-charts-python
- **Multi-day Support**: Display data for multiple trading days (--days parameter)

## Key Features Implemented

1. **CSV Data Loading**: Parse CSV files with specific datetime format (GMT+timezone)
2. **Exchange Calendar Integration**: Get official trading hours for different exchanges
3. **Timezone Handling**: Convert timezone-aware data to local time for proper chart display
4. **Trading Hours Filtering**: Show only data during official market hours
5. **Multi-day Support**: Load and display multiple trading days with --days parameter
6. **Auto-fit Charts**: Automatically scale chart view to show all data properly
7. **Modular Architecture**: Clean separation of concerns across multiple modules

## Command Line Interface

```bash
python main.py --input data.csv --exchange XFRA [--days 3] [--verbose]
```

## Technical Stack

- **Python 3.x**
- **pandas**: CSV data processing
- **lightweight-charts-python**: Interactive charting
- **exchange_calendars**: Trading hours and exchange information
- **configparser**: Configuration management
- **logging**: Comprehensive logging system

## Project Structure

```
plot-stock-charts/
├── main.py                 # Main application entry point
├── src/
│   ├── data/              # Data handling modules
│   ├── exchange/          # Exchange calendar integration
│   ├── chart/             # Chart plotting functionality
│   └── utils/             # Utility functions
├── settings.ini           # Configuration file
└── requirements.txt       # Python dependencies
```

## Success Criteria

- ✅ Load CSV data with custom datetime format
- ✅ Filter data to trading hours for specified exchange
- ✅ Display interactive candlestick charts
- ✅ Support multiple trading days
- ✅ Handle timezone conversions properly
- ✅ Auto-fit chart view for optimal display
- ✅ Comprehensive error handling and logging
