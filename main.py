"""
Stock Chart Plotter - Main Application

A command-line application for plotting stock charts from CSV data
with exchange-specific trading hours filtering.

Usage:
    python main.py --input data.csv --exchange XETR
"""

import argparse
import logging
import sys
import configparser
from pathlib import Path
from datetime import datetime

from src.data.csv_reader import CSVReader
from src.exchange.calendar import ExchangeCalendar
from src.chart.plotter import StockChartPlotter
from src.output.json_exporter import JSONExporter
from src.indicators.parser import IndicatorParser
from src.indicators.calculator import IndicatorCalculator
from src.indicators.renderer import IndicatorRenderer
from src.lines.parser import LineParser
from src.lines.renderer import LineRenderer
from src.utils.date_utils import format_date_for_display, DateTimeHelper


def setup_logging(config_path: str = "settings.ini") -> None:
    """
    Set up logging configuration.
    
    Args:
        config_path: Path to the configuration file
    """
    config = configparser.ConfigParser()
    
    # Load configuration
    if Path(config_path).exists():
        config.read(config_path)
    
    # Get logging settings
    log_level = config.get('LOGGING', 'level', fallback='INFO')
    log_format = config.get('LOGGING', 'format', 
                           fallback='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Plot stock charts from CSV data with exchange trading hours filtering',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Display interactive chart
  python main.py --input data.csv --exchange XETR
  python main.py --input stock_data.csv --exchange NYSE --days 3
  
  # Display chart with technical indicators
  python main.py --input data.csv --exchange XETR --indicators ema_50|red,ema_200|green
  python main.py --input data.csv --exchange XETR --days 3 --indicators ema_50|#FF0000,ema_200|blue
  
  # Export to JSON instead of displaying chart
  python main.py --input data.csv --exchange XETR --output chart.json
  python main.py --input data.csv --exchange XETR --days 3 --output chart.json --indicators ema_50|red,ema_200|green
  
Supported exchanges include: XETR (Xetra), NYSE, NASDAQ, LSE, etc.
Use exchange_calendars library documentation for full list.
        """
    )
    
    parser.add_argument(
        '--input',
        required=True,
        help='Path to the input CSV file containing OHLCV data'
    )
    
    parser.add_argument(
        '--exchange',
        required=True,
        help='Exchange code (e.g., XETR for Xetra, NYSE for New York Stock Exchange)'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=1,
        help='Number of latest trading days to display (default: 1)'
    )
    
    parser.add_argument(
        '--config',
        default='settings.ini',
        help='Path to configuration file (default: settings.ini)'
    )
    
    parser.add_argument(
        '--output',
        help='Output JSON file path (if specified, chart will not be displayed)'
    )
    
    parser.add_argument(
        '--indicators',
        help='Technical indicators to display (format: ema_50|red,ema_200|green)'
    )
    
    parser.add_argument(
        '--lines',
        help='Horizontal lines to display (format: label|value|color|width)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()


def validate_inputs(args: argparse.Namespace) -> None:
    """
    Validate command-line arguments.
    
    Args:
        args: Parsed arguments
        
    Raises:
        SystemExit: If validation fails
    """
    logger = logging.getLogger(__name__)
    
    # Check if input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)
    
    if not input_path.suffix.lower() == '.csv':
        logger.error(f"Input file must be a CSV file: {args.input}")
        sys.exit(1)
    
    # Validate exchange code by trying to create calendar
    try:
        ExchangeCalendar(args.exchange)
        logger.info(f"Exchange code '{args.exchange}' is valid")
    except ValueError as e:
        logger.error(f"Invalid exchange code '{args.exchange}': {e}")
        logger.info("Use exchange_calendars library documentation for supported exchanges")
        sys.exit(1)
    
    # Validate output path if provided
    if args.output:
        json_exporter = JSONExporter(args.config)
        if not json_exporter.validate_output_path(args.output):
            logger.error(f"Invalid output path: {args.output}")
            sys.exit(1)


def main() -> None:
    """
    Main application entry point.
    """
    # Parse arguments
    args = parse_arguments()
    
    # Set up logging
    setup_logging(args.config)
    logger = logging.getLogger(__name__)
    
    # Override log level if verbose
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    logger.info("Starting Stock Chart Plotter")
    logger.info(f"Input file: {args.input}")
    logger.info(f"Exchange: {args.exchange}")
    
    try:
        # Validate inputs
        validate_inputs(args)
        
        # Initialize components
        logger.info("Initializing components...")
        csv_reader = CSVReader(args.config)
        exchange_calendar = ExchangeCalendar(args.exchange)
        chart_plotter = StockChartPlotter(args.config)
        date_helper = DateTimeHelper()
        
        # Process indicators first if specified (need full dataset)
        indicators_data = {}
        indicators_config = []
        indicators_metadata = []
        full_dataset = None
        
        if args.indicators:
            try:
                logger.info(f"Processing indicators: {args.indicators}")
                logger.info("Loading full dataset for indicator calculations...")
                
                # Load the complete dataset for indicator calculations
                full_dataset = csv_reader.load_all_data(args.input)
                
                if not full_dataset or len(full_dataset) == 0:
                    raise ValueError("No data found in CSV file for indicator calculations")
                
                logger.info(f"Loaded {len(full_dataset)} data points for indicator calculations")
                
                # Parse indicators
                indicator_parser = IndicatorParser()
                indicators_config = indicator_parser.parse_indicators(args.indicators)
                
                # Validate periods against full dataset
                indicators_config = indicator_parser.validate_periods_against_data(indicators_config, len(full_dataset))
                
                if indicators_config:
                    # Calculate indicators on full dataset
                    indicator_calculator = IndicatorCalculator()
                    indicators_config = indicator_calculator.validate_data_sufficiency(full_dataset, indicators_config)
                    indicators_data = indicator_calculator.calculate_indicators(full_dataset, indicators_config)
                    indicators_metadata = indicator_calculator.get_indicator_metadata(indicators_config)
                    
                    logger.info(f"Successfully calculated {len(indicators_data)} indicators on full dataset")
                else:
                    logger.warning("No valid indicators after validation")
                    
            except ImportError as e:
                logger.error(f"TA-Lib not available: {e}")
                logger.info("Install TA-Lib to use technical indicators")
                sys.exit(1)
            except Exception as e:
                logger.error(f"Failed to process indicators: {e}")
                if args.verbose:
                    logger.exception("Indicator processing error details:")
                sys.exit(1)
        
        # Load data from CSV for display
        logger.info("Loading data from CSV for display...")
        
        if args.days == 1:
            # Single day mode (original behavior)
            dataset = csv_reader.get_latest_trading_day_data(args.input)
            
            if not dataset:
                logger.error("No data found in CSV file")
                sys.exit(1)
            
            # Get the latest date
            latest_date = dataset.get_latest_date()
            if latest_date is None:
                logger.error("No valid dates found in the dataset")
                sys.exit(1)
                
            logger.info(f"Latest trading day in data: {format_date_for_display(latest_date)}")
            
        else:
            # Multi-day mode
            logger.info(f"Loading data for {args.days} trading days...")
            
            # First, get the latest date from the CSV
            temp_dataset = csv_reader.get_latest_trading_day_data(args.input)
            if not temp_dataset:
                logger.error("No data found in CSV file")
                sys.exit(1)
            
            latest_date = temp_dataset.get_latest_date()
            if latest_date is None:
                logger.error("No valid dates found in the dataset")
                sys.exit(1)
            
            # Get the list of trading days
            trading_days = exchange_calendar.get_latest_trading_days(latest_date, args.days)
            
            if not trading_days:
                logger.error(f"Could not find {args.days} trading days")
                sys.exit(1)
            
            logger.info(f"Loading data for trading days: {[format_date_for_display(d) for d in trading_days]}")
            
            # Load data for all trading days
            dataset = csv_reader.get_latest_days_data(args.input, trading_days)
            
            if not dataset:
                logger.error("No data found for the specified trading days")
                sys.exit(1)
        
        # Debug: Log original data info
        logger.info(f"DEBUG: Original data has {len(dataset)} data points")
        if dataset:
            first_time = dataset.data[0].timestamp
            last_time = dataset.data[-1].timestamp
            logger.info(f"DEBUG: Original data time range: {first_time} to {last_time}")
        
        # For multi-day mode, we need to filter each day separately
        if args.days == 1:
            # Single day filtering (original behavior)
            try:
                logger.info("Filtering data to official trading hours...")
                filtered_data = exchange_calendar.filter_trading_hours(dataset, latest_date)
                
                # Debug: Log filtered data info
                if filtered_data:
                    logger.info(f"DEBUG: Filtered data has {len(filtered_data)} data points")
                    first_time = filtered_data.data[0].timestamp
                    last_time = filtered_data.data[-1].timestamp
                    logger.info(f"DEBUG: Filtered data time range: {first_time} to {last_time}")
                
                if not filtered_data:
                    logger.warning("No data found during official trading hours, using all available data for the day")
                    filtered_data = dataset
                    
            except ValueError as e:
                # Exchange is closed on this date
                logger.warning(f"Exchange {args.exchange} is closed on {format_date_for_display(latest_date)}: {e}")
                logger.info("Displaying all available data for the day")
                filtered_data = dataset
        else:
            # Multi-day filtering - filter each day's trading hours and combine
            logger.info("Filtering multi-day data to official trading hours...")
            all_filtered_data = []
            
            for trading_day in trading_days:
                # Get data for this specific day
                day_dataset = dataset.filter_by_date(datetime.combine(trading_day, datetime.min.time()))
                
                if day_dataset:
                    try:
                        # Filter this day's data to trading hours
                        day_filtered = exchange_calendar.filter_trading_hours(day_dataset, trading_day)
                        if day_filtered:
                            all_filtered_data.extend(day_filtered.data)
                            logger.info(f"Filtered {len(day_filtered)} data points for {format_date_for_display(trading_day)}")
                        else:
                            logger.warning(f"No trading hours data for {format_date_for_display(trading_day)}, using all data")
                            all_filtered_data.extend(day_dataset.data)
                    except ValueError:
                        logger.warning(f"Exchange closed on {format_date_for_display(trading_day)}, using all data")
                        all_filtered_data.extend(day_dataset.data)
            
            from src.data.data_models import StockDataset
            filtered_data = StockDataset(all_filtered_data) if all_filtered_data else dataset
        
        if not filtered_data:
            logger.error("No data available during trading hours")
            sys.exit(1)
        
        # Filter indicators data to match the filtered display data
        filtered_indicators_data = {}
        if indicators_data and filtered_data:
            logger.info("Filtering indicators to match display data...")
            indicator_renderer = IndicatorRenderer()
            
            # Create timestamp mapping for filtered data
            filtered_timestamps = {point.timestamp for point in filtered_data.data}
            
            # Filter each indicator's data to match filtered timestamps
            for indicator_name, indicator_points in indicators_data.items():
                filtered_points = [
                    (timestamp, value) for timestamp, value in indicator_points
                    if timestamp in filtered_timestamps
                ]
                filtered_indicators_data[indicator_name] = filtered_points
                
                valid_count = sum(1 for _, val in filtered_points if val is not None)
                logger.info(f"Filtered {indicator_name}: {valid_count} valid points for display")
        
        # Process horizontal lines if specified
        lines_data = []
        if args.lines:
            try:
                logger.info(f"Processing horizontal lines: {args.lines}")
                
                # Parse horizontal lines
                line_parser = LineParser()
                lines_data = line_parser.parse_lines(args.lines)
                
                logger.info(f"Successfully parsed {len(lines_data)} horizontal lines")
                
            except Exception as e:
                logger.error(f"Failed to process horizontal lines: {e}")
                if args.verbose:
                    logger.exception("Horizontal lines processing error details:")
                sys.exit(1)
        
        # Check if JSON output is requested
        if args.output:
            # Export to JSON instead of displaying chart
            logger.info(f"Exporting data to JSON file: {args.output}")
            
            # Initialize JSON exporter
            json_exporter = JSONExporter(args.config)
            
            # Prepare additional metadata
            metadata = {
                "input_file": args.input,
                "latest_date": format_date_for_display(latest_date),
                "filtered_to_trading_hours": True
            }
            
            # Add indicators metadata if available
            if indicators_metadata:
                metadata["indicators"] = indicators_metadata
            
            # Add lines as key-value pairs if available
            if lines_data:
                lines_keyvalues = {}
                for label, value, color, width in lines_data:
                    lines_keyvalues[label] = value
                metadata["lines"] = lines_keyvalues
            
            # Prepare indicators data for JSON export
            indicators_for_json = []
            if filtered_indicators_data:
                indicator_renderer = IndicatorRenderer()
                indicators_for_json = indicator_renderer.prepare_indicators_for_json(filtered_indicators_data, filtered_data)
            
            # Export to JSON
            json_exporter.export_to_json(
                dataset=filtered_data,
                output_path=args.output,
                exchange_code=args.exchange,
                days=args.days,
                metadata=metadata,
                indicators_data=indicators_for_json
            )
            
            logger.info("JSON export completed successfully.")
            
        else:
            # Create and display chart with indicators
            logger.info("Creating chart...")
            chart_plotter.plot_candlestick_chart(
                dataset=filtered_data,
                title="Stock Price Chart",
                exchange_code=args.exchange,
                date_str=format_date_for_display(latest_date)
            )
            
            # Add indicators to chart if available
            if filtered_indicators_data and indicators_config:
                logger.info("Adding indicators to chart...")
                indicator_renderer = IndicatorRenderer()
                
                # Validate chart compatibility
                if indicator_renderer.validate_chart_compatibility(chart_plotter.chart):
                    indicator_renderer.add_indicators_to_chart(
                        chart_plotter.chart, 
                        filtered_indicators_data, 
                        indicators_config
                    )
                    logger.info("Indicators added successfully")
                else:
                    logger.warning("Chart does not support indicators, displaying without them")
            
            # Add horizontal lines to chart if available
            if lines_data:
                logger.info("Adding horizontal lines to chart...")
                line_renderer = LineRenderer()
                
                # Validate chart compatibility
                if line_renderer.validate_chart_compatibility(chart_plotter.chart):
                    line_renderer.add_horizontal_lines_to_chart(
                        chart_plotter.chart, 
                        lines_data
                    )
                    logger.info("Horizontal lines added successfully")
                else:
                    logger.warning("Chart does not support horizontal lines, displaying without them")
            
            logger.info("Displaying chart... (Close the chart window to exit)")
            chart_plotter.show_chart(block=True)
            
            logger.info("Chart closed. Application finished successfully.")
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            logger.exception("Full error details:")
        sys.exit(1)


if __name__ == '__main__':
    main()
