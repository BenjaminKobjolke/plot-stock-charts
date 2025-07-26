"""
CSV reader for stock data.

This module handles loading and parsing CSV files containing OHLCV stock data.
"""

import pandas as pd
from datetime import datetime, date
from typing import List, Optional
import logging
import configparser
from pathlib import Path

from .data_models import OHLCVData, StockDataset


class CSVReader:
    """
    Handles reading and parsing CSV files with stock data.
    
    Supports the specific datetime format used in the input CSV files.
    """
    
    def __init__(self, config_path: str = "settings.ini"):
        """
        Initialize the CSV reader with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config = configparser.ConfigParser()
        
        # Load configuration
        if Path(config_path).exists():
            self.config.read(config_path)
        else:
            self.logger.warning(f"Configuration file {config_path} not found, using defaults")
        
        # Get date format from config or use default
        self.date_format = self.config.get('DATA', 'date_format', 
                                         fallback='%d.%m.%Y %H:%M:%S.%f GMT%z')
    
    def parse_datetime(self, datetime_str: str) -> datetime:
        """
        Parse datetime string from CSV format.
        
        Args:
            datetime_str: Datetime string in format "01.07.2025 00:00:00.000 GMT+0200"
            
        Returns:
            Parsed datetime object
            
        Raises:
            ValueError: If datetime string cannot be parsed
        """
        try:
            # Handle the specific format from the CSV
            # Remove "GMT" prefix and parse
            cleaned_str = datetime_str.replace("GMT", "")
            return datetime.strptime(cleaned_str, '%d.%m.%Y %H:%M:%S.%f %z')
        except ValueError as e:
            self.logger.error(f"Failed to parse datetime '{datetime_str}': {e}")
            raise ValueError(f"Invalid datetime format: {datetime_str}") from e
    
    def load_csv(self, file_path: str) -> StockDataset:
        """
        Load stock data from CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            StockDataset containing the loaded data
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If the CSV format is invalid
        """
        try:
            # Check if file exists
            if not Path(file_path).exists():
                raise FileNotFoundError(f"CSV file not found: {file_path}")
            
            # Read CSV file
            self.logger.info(f"Loading CSV file: {file_path}")
            df = pd.read_csv(file_path)
            
            # Validate required columns
            required_columns = ['Local time', 'Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Parse data
            ohlcv_data = []
            for _, row in df.iterrows():
                try:
                    timestamp = self.parse_datetime(row['Local time'])
                    
                    data_point = OHLCVData(
                        timestamp=timestamp,
                        open=float(row['Open']),
                        high=float(row['High']),
                        low=float(row['Low']),
                        close=float(row['Close']),
                        volume=float(row['Volume'])
                    )
                    
                    ohlcv_data.append(data_point)
                    
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Skipping invalid row: {row.to_dict()}, Error: {e}")
                    continue
            
            if not ohlcv_data:
                raise ValueError("No valid data found in CSV file")
            
            self.logger.info(f"Successfully loaded {len(ohlcv_data)} data points")
            return StockDataset(ohlcv_data)
            
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty")
        except pd.errors.ParserError as e:
            raise ValueError(f"Failed to parse CSV file: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error loading CSV: {e}")
            raise
    
    def get_latest_trading_day_data(self, file_path: str) -> StockDataset:
        """
        Load CSV and return only data from the latest trading day.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            StockDataset containing only the latest day's data
        """
        # Load all data
        full_dataset = self.load_csv(file_path)
        
        # Get the latest date
        latest_date = full_dataset.get_latest_date()
        if latest_date is None:
            raise ValueError("No data found in CSV file")
        
        # Filter to latest date
        latest_day_data = full_dataset.filter_by_date(datetime.combine(latest_date, datetime.min.time()))
        
        self.logger.info(f"Extracted {len(latest_day_data)} data points for latest trading day: {latest_date}")
        return latest_day_data
    
    def get_latest_days_data(self, file_path: str, trading_days: List[date]) -> StockDataset:
        """
        Load CSV and return data for the specified trading days.
        
        Args:
            file_path: Path to the CSV file
            trading_days: List of dates to include (in chronological order)
            
        Returns:
            StockDataset containing data for all specified days
        """
        # Load all data
        full_dataset = self.load_csv(file_path)
        
        if not trading_days:
            self.logger.warning("No trading days specified")
            return StockDataset([])
        
        # Collect data for all specified days
        all_days_data = []
        
        for trading_day in trading_days:
            # Filter to this specific date
            day_data = full_dataset.filter_by_date(datetime.combine(trading_day, datetime.min.time()))
            
            if day_data:
                all_days_data.extend(day_data.data)
                self.logger.info(f"Found {len(day_data)} data points for {trading_day}")
            else:
                self.logger.warning(f"No data found for trading day: {trading_day}")
        
        if not all_days_data:
            self.logger.warning("No data found for any of the specified trading days")
            return StockDataset([])
        
        result_dataset = StockDataset(all_days_data)
        self.logger.info(f"Extracted {len(result_dataset)} total data points for {len(trading_days)} trading days")
        return result_dataset
