# Active Context - Stock Chart Plotter

## Current Status

The Stock Chart Plotter application is **fully functional** with all core features implemented and working correctly. **NEW**: JSON output functionality has been added as requested.

## Recent Achievements

### 1. Multi-day Support Implementation ✅

- Added `--days` parameter to command line interface
- Implemented `get_latest_trading_days()` method in ExchangeCalendar class
- Created `get_latest_days_data()` method in CSVReader class
- Updated main.py to handle both single-day and multi-day modes
- Successfully tested with `--days 3` parameter

### 2. Timezone Issue Resolution ✅

- **Problem**: Chart was displaying UTC times (7:00-15:30) instead of local times (9:00-17:30)
- **Solution**: Modified `to_lightweight_charts_format()` to strip timezone info and use local time values
- **Result**: Chart now correctly displays local trading hours (9:00 AM - 5:30 PM)

### 3. Chart Auto-fit Feature ✅

- **Problem**: Chart was starting with data compressed to one side, showing mostly empty space
- **Solution**: Added `chart.fit()` call after setting data to auto-scale the view
- **Result**: Chart now automatically fits all data in the visible area on startup

### 4. JSON Output Mode Implementation ✅ **NEW**

- **Requirement**: User requested JSON output mode as alternative to chart display
- **Implementation**:
  - Created new `src/output/json_exporter.py` module with `JSONExporter` class
  - Added `--output` parameter to command line interface
  - Modified main.py to conditionally export JSON instead of displaying chart
  - JSON includes comprehensive metadata and structured OHLCV data
- **Features**:
  - Structured JSON with metadata section (export timestamp, exchange, data count, time range)
  - ISO format timestamps for easy parsing
  - Validation of output path with helpful error messages
  - Works with both single-day and multi-day modes
- **Usage**: `python main.py --input input.csv --exchange XETR --days 3 --output chart.json`

## Current Working Features

### Core Functionality

- ✅ CSV data loading with custom datetime format parsing
- ✅ Exchange calendar integration (XFRA, XETR, etc.)
- ✅ Trading hours filtering per exchange
- ✅ Interactive candlestick chart display
- ✅ **JSON data export with comprehensive metadata** ✅ **NEW**
- ✅ Timezone conversion (GMT+0200 to local display)
- ✅ Multi-day data loading and display
- ✅ Auto-fit chart view

### Command Line Interface

```bash
# Display interactive chart (default behavior)
python main.py --input input.csv --exchange XFRA
python main.py --input input.csv --exchange XFRA --days 3
python main.py --input input.csv --exchange XFRA --days 3 --verbose

# Export to JSON (no chart displayed)
python main.py --input input.csv --exchange XFRA --output chart.json
python main.py --input input.csv --exchange XFRA --days 3 --output chart.json
```

## Technical Implementation Details

### Data Flow

1. **CSV Loading**: Parse CSV with GMT+timezone format
2. **Exchange Calendar**: Get official trading hours in UTC
3. **Data Filtering**: Filter each day's data to trading hours
4. **Timezone Conversion**: Convert to naive timestamps for chart display
5. **Chart Rendering**: Display with auto-fit scaling

### Key Classes and Methods

- `CSVReader.get_latest_days_data()`: Load multiple days of data
- `ExchangeCalendar.get_latest_trading_days()`: Find N trading days back
- `ExchangeCalendar.filter_trading_hours()`: Filter to official hours
- `StockChartPlotter.plot_candlestick_chart()`: Render with auto-fit
- `JSONExporter.export_to_json()`: Export filtered data to structured JSON format **NEW**

## Debug Information Available

- Original data point count and time range
- Trading hours from exchange calendar (with timezone info)
- Filtered data point count and time range
- Chart data timestamps after timezone conversion
- Auto-fit application status

## Known Working Configurations

- **Exchange**: XFRA (Frankfurt)
- **Data Format**: CSV with "Local time" column in format "01.07.2025 00:00:00.000 GMT+0200"
- **Time Intervals**: 15-minute OHLCV data
- **Days**: Successfully tested with 1 and 3 days

## Next Potential Enhancements

- Volume subplot display
- Additional exchange support testing
- Chart export functionality
- Custom time range selection
- Different chart themes/styling options

## Project Health

- **Status**: ✅ Fully Functional
- **Test Coverage**: Manual testing completed
- **Error Handling**: Comprehensive logging and error handling in place
- **Code Quality**: Modular architecture with clean separation of concerns
