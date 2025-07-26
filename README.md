# Stock Chart Plotter

A Python application for plotting interactive stock charts from CSV data with exchange-specific trading hours filtering.

You can download csv files here:

https://www.dukascopy.com/trading-tools/widgets/quotes/historical_data_feed

## Features

- Load OHLCV (Open, High, Low, Close, Volume) data from CSV files
- Filter data to show only the latest trading day or multiple trading days
- Apply exchange-specific trading hours filtering using official exchange calendars
- Display interactive candlestick charts using lightweight-charts-python
- **Technical indicators with EMA (Exponential Moving Average) overlays**
- **Horizontal lines for support/resistance levels with custom labels**
- **Export filtered data to JSON format for external use**
- Support for multiple stock exchanges worldwide
- Configurable chart appearance and logging
- Modular, well-documented codebase

## Requirements

- Python 3.7+
- pandas
- lightweight-charts-python
- exchange-calendars
- pytz
- TA-Lib (for technical indicators)

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line

```bash
python main.py --input your_data.csv --exchange XETR
```

### Using the Batch File (Windows)

```bash
run.bat input.csv XETR
```

### Arguments

- `--input`: Path to the input CSV file containing OHLCV data (required)
- `--exchange`: Exchange code (e.g., XETR for Xetra, NYSE for New York Stock Exchange) (required)
- `--days`: Number of latest trading days to display (optional, default: 1)
- `--indicators`: Technical indicators to display (optional, format: `ema_50|red,ema_200|green`)
- `--lines`: Horizontal lines to display (optional, format: `label|value|color|width`)
- `--output`: Output JSON file path (optional, if specified, chart will not be displayed)
- `--config`: Path to configuration file (optional, default: settings.ini)
- `--verbose`, `-v`: Enable verbose logging (optional)

### Supported Exchange Codes

The application uses the `exchange_calendars` library, which supports many exchanges including:

- **XETR**: Xetra (Germany)
- **NYSE**: New York Stock Exchange (USA)
- **NASDAQ**: NASDAQ (USA)
- **LSE**: London Stock Exchange (UK)
- **TSE**: Tokyo Stock Exchange (Japan)
- **HKEX**: Hong Kong Stock Exchange
- **SSE**: Shanghai Stock Exchange (China)
- **BSE**: Bombay Stock Exchange (India)

For a complete list, refer to the [exchange_calendars documentation](https://github.com/gerrymanoim/exchange_calendars).

## CSV Data Format

The input CSV file should have the following columns:

```csv
Local time,Open,High,Low,Close,Volume
01.07.2025 00:00:00.000 GMT+0200,25552,25552,25552,25552,0
```

### Required Columns

- **Local time**: Timestamp in format "DD.MM.YYYY HH:MM:SS.fff GMT±HHMM"
- **Open**: Opening price
- **High**: Highest price during the period
- **Low**: Lowest price during the period
- **Close**: Closing price
- **Volume**: Trading volume

## Configuration

The application uses a `settings.ini` file for configuration:

```ini
[DATA]
date_format = %d.%m.%Y %H:%M:%S.%f GMT%z

[CHART]
width = 1200
height = 600
theme = dark

[LOGGING]
level = INFO
format = %(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Configuration Sections

- **DATA**: Data parsing settings
- **CHART**: Chart appearance settings
- **LOGGING**: Logging configuration

## How It Works

1. **Data Loading**: The application loads the CSV file and parses the datetime format
2. **Latest Day Extraction**: Identifies and extracts data from the most recent trading day
3. **Exchange Calendar**: Uses the specified exchange's official calendar to get trading hours
4. **Time Filtering**: Filters the data to only include timestamps during official trading hours
5. **Chart Creation**: Creates an interactive candlestick chart using lightweight-charts-python
6. **Display**: Shows the chart in a web browser window

## Project Structure

```
plot-stock-charts/
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── data_models.py      # Data structures for OHLCV data
│   │   └── csv_reader.py       # CSV file loading and parsing
│   ├── exchange/
│   │   ├── __init__.py
│   │   └── calendar.py         # Exchange calendar integration
│   ├── chart/
│   │   ├── __init__.py
│   │   └── plotter.py          # Chart creation and display
│   ├── indicators/
│   │   ├── __init__.py
│   │   ├── parser.py           # Parse indicator specifications
│   │   ├── calculator.py       # TA-Lib indicator calculations
│   │   └── renderer.py         # Add indicators to charts
│   ├── lines/
│   │   ├── __init__.py
│   │   ├── parser.py           # Parse horizontal line specifications
│   │   └── renderer.py         # Add horizontal lines to charts
│   ├── output/
│   │   ├── __init__.py
│   │   └── json_exporter.py    # JSON export functionality
│   ├── utils/
│   │   ├── __init__.py
│   │   └── date_utils.py       # Date/time utility functions
│   └── __init__.py
├── main.py                     # Main application entry point
├── run.bat                     # Windows batch file for easy execution
├── requirements.txt            # Python dependencies
├── settings.ini               # Configuration file
└── README.md                  # This file
```

## Examples

### Display Interactive Chart

```bash
# Single day chart
python main.py --input stock_data.csv --exchange XETR

# Multi-day chart (3 days)
python main.py --input stock_data.csv --exchange XETR --days 3

# With verbose logging
python main.py --input stock_data.csv --exchange NYSE --verbose
```

### Technical Indicators

```bash
# Chart with EMA indicators
python main.py --input stock_data.csv --exchange XETR --indicators ema_50|red,ema_200|green

# Multi-day chart with indicators
python main.py --input stock_data.csv --exchange XETR --days 3 --indicators ema_50|#FF0000,ema_200|blue

# Indicators with custom colors (hex codes)
python main.py --input stock_data.csv --exchange XETR --indicators ema_50|#FF6B35,ema_200|#004E89
```

#### Supported Indicators

- **EMA (Exponential Moving Average)**: `ema_[period]` (e.g., `ema_50`, `ema_200`)

#### Color Options

- **Named Colors**: `red`, `green`, `blue`, `yellow`, `orange`, `purple`, `cyan`, `magenta`, `black`, `white`, `gray`
- **Hex Colors**: Any valid hex color code (e.g., `#FF0000`, `#00FF00`, `#0000FF`)

#### Indicator Format

The `--indicators` parameter uses the format: `indicator_period|color,indicator_period|color`

Examples:

- `ema_50|red` - 50-period EMA in red
- `ema_200|#00FF00` - 200-period EMA in green (hex)
- `ema_50|red,ema_200|green` - Both indicators with different colors

### Horizontal Lines

```bash
# Basic horizontal lines (random colors assigned)
python main.py --input stock_data.csv --exchange XETR --lines "Support|28.7,Resistance|29.5"

# Lines with specific colors
python main.py --input stock_data.csv --exchange XETR --lines "Support|28.7|blue,Resistance|29.5|red"

# Lines with custom widths
python main.py --input stock_data.csv --exchange XETR --lines "Support|28.7|blue|3,Resistance|29.5|red|1"

# Combined with indicators
python main.py --input stock_data.csv --exchange XETR --indicators ema_50|red --lines "Support|28.7,Target|29.5"

# Multiple lines with mixed specifications
python main.py --input stock_data.csv --exchange XETR --lines "Support|28.7|green|5,Resistance|29.5,Target|30.2|red|2"
```

#### Line Format

The `--lines` parameter uses the format: `label|value|color|width`

- **Required**: label, value
- **Optional**: color (smart random if missing), width (defaults to 1)

#### Color Options (Same as Indicators)

- **Named Colors**: `red`, `green`, `blue`, `yellow`, `orange`, `purple`, `cyan`, `magenta`, `black`, `white`, `gray`
- **Hex Colors**: Any valid hex color code (e.g., `#FF0000`, `#00FF00`, `#0000FF`)
- **Smart Random**: Automatically assigns visually distinct colors when not specified

#### Line Examples

- `"Support|28.7"` - Label "Support" at 28.7, random color, width 1
- `"Support|28.7|blue"` - Label "Support" at 28.7, blue color, width 1
- `"Support|28.7|blue|3"` - Label "Support" at 28.7, blue color, width 3
- `"Support|28.7,Resistance|29.5"` - Multiple lines with random colors

#### Smart Color Assignment

When colors are not specified, the system automatically:

1. **Picks unused colors** from a predefined pool for visual distinction
2. **Avoids duplicates** when possible
3. **Falls back to random selection** if all colors are used
4. **Ensures visual clarity** with a diverse color palette

### Export to JSON

```bash
# Export single day data to JSON
python main.py --input stock_data.csv --exchange XETR --output chart.json

# Export multi-day data to JSON
python main.py --input stock_data.csv --exchange XETR --days 3 --output chart.json

# Export with indicators included
python main.py --input stock_data.csv --exchange XETR --indicators ema_50|red,ema_200|green --output chart.json

# Export with verbose logging
python main.py --input stock_data.csv --exchange NYSE --days 3 --output data.json --verbose
```

### JSON Output Format

When using the `--output` parameter, the application generates a structured JSON file:

```json
{
  "metadata": {
    "export_timestamp": "2025-07-26T12:00:00",
    "exchange_code": "XETR",
    "days_requested": 3,
    "data_points_count": 156,
    "time_range": {
      "start": "2025-07-24T09:00:00",
      "end": "2025-07-26T17:30:00"
    },
    "data_format": "OHLCV",
    "timezone_info": "Local time (timezone information removed for cleaner output)",
    "input_file": "input.csv",
    "latest_date": "26.07.2025",
    "filtered_to_trading_hours": true
  },
  "data": [
    {
      "timestamp": "2025-07-24T09:00:00",
      "open": 25552.0,
      "high": 25565.0,
      "low": 25540.0,
      "close": 25558.0,
      "volume": 1250
    }
  ]
}
```

### Using Custom Configuration

```bash
python main.py --input data.csv --exchange LSE --config my_config.ini
```

## Error Handling

The application includes comprehensive error handling for:

- Missing or invalid CSV files
- Unsupported exchange codes
- Invalid date formats
- Empty datasets
- Exchange closure days
- Network issues (for exchange calendar data)

## Logging

The application provides detailed logging information including:

- Data loading progress
- Exchange calendar information
- Trading hours filtering results
- Chart creation status
- Error messages and warnings

## Troubleshooting

### Common Issues

1. **"Exchange code not supported"**

   - Check the exchange code spelling
   - Refer to exchange_calendars documentation for valid codes

2. **"No data found during trading hours"**

   - The exchange might be closed on the data date
   - Check if the date in your CSV is a trading day

3. **"Invalid datetime format"**

   - Ensure your CSV uses the expected datetime format
   - Check the date_format setting in settings.ini

4. **Chart not displaying**
   - Ensure lightweight-charts-python is properly installed
   - Check if your system can open web browser windows

### Getting Help

1. Run with `--verbose` flag for detailed logging
2. Check the console output for specific error messages
3. Verify your CSV file format matches the expected structure
4. Ensure all required dependencies are installed

## License

This project is provided as-is for educational and personal use.

## Contributing

This is a standalone application. For modifications:

1. Follow the existing code structure and patterns
2. Add appropriate logging and error handling
3. Update documentation as needed
4. Test with various CSV formats and exchange codes
