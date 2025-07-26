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
  python main.py --input data.csv --exchange XETR
  python main.py --input stock_data.csv --exchange NYSE
  
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
        
        # Load data from CSV
        logger.info("Loading data from CSV...")
        
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
        
        # Create and display chart
        logger.info("Creating chart...")
        chart_plotter.plot_candlestick_chart(
            dataset=filtered_data,
            title="Stock Price Chart",
            exchange_code=args.exchange,
            date_str=format_date_for_display(latest_date)
        )
        
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
