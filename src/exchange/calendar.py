"""
Exchange calendar integration for trading hours.

This module provides functionality to get official trading hours
for different stock exchanges using the exchange_calendars library.
"""

import exchange_calendars as xcals
from datetime import datetime, date, time
from typing import Tuple, Optional
import logging
import pytz

from ..data.data_models import StockDataset


class ExchangeCalendar:
    """
    Handles exchange calendar operations and trading hours filtering.
    
    Uses the exchange_calendars library to get official trading hours
    for different stock exchanges.
    """
    
    def __init__(self, exchange_code: str):
        """
        Initialize with a specific exchange.
        
        Args:
            exchange_code: Exchange code (e.g., 'XETR' for Xetra)
            
        Raises:
            ValueError: If exchange code is not supported
        """
        self.logger = logging.getLogger(__name__)
        self.exchange_code = exchange_code.upper()
        
        try:
            self.calendar = xcals.get_calendar(self.exchange_code)
            self.logger.info(f"Initialized calendar for exchange: {self.exchange_code}")
        except Exception as e:
            self.logger.error(f"Failed to initialize calendar for {self.exchange_code}: {e}")
            raise ValueError(f"Unsupported exchange code: {self.exchange_code}") from e
    
    def get_trading_hours(self, target_date: date) -> Optional[Tuple[datetime, datetime]]:
        """
        Get trading hours for a specific date.
        
        Args:
            target_date: The date to get trading hours for
            
        Returns:
            Tuple of (open_time, close_time) as datetime objects,
            or None if the exchange is closed on that date
        """
        try:
            # Convert date to string format expected by exchange_calendars
            date_str = target_date.strftime('%Y-%m-%d')
            
            # Get the schedule for the specific date
            schedule = self.calendar.schedule.loc[date_str:date_str]
            
            if schedule.empty:
                self.logger.warning(f"No trading schedule found for {target_date}")
                return None
            
            # Get the first (and should be only) row
            trading_day = schedule.iloc[0]
            
            # Use 'open' and 'close' columns instead of 'market_open' and 'market_close'
            open_time = trading_day['open']
            close_time = trading_day['close']
            
            # Convert to datetime objects
            if pd.isna(open_time) or pd.isna(close_time):
                self.logger.info(f"Exchange {self.exchange_code} is closed on {target_date}")
                return None
            
            # Convert pandas Timestamp to datetime
            open_dt = open_time.to_pydatetime()
            close_dt = close_time.to_pydatetime()
            
            # Debug: Log timezone information
            self.logger.info(f"DEBUG: Raw trading hours from exchange_calendars:")
            self.logger.info(f"DEBUG: Open: {open_dt} (timezone: {open_dt.tzinfo})")
            self.logger.info(f"DEBUG: Close: {close_dt} (timezone: {close_dt.tzinfo})")
            
            self.logger.info(f"Trading hours for {target_date}: {open_dt} - {close_dt}")
            return (open_dt, close_dt)
            
        except KeyError as e:
            self.logger.warning(f"No trading data available for {target_date}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting trading hours for {target_date}: {e}")
            return None
    
    def is_trading_day(self, target_date: date) -> bool:
        """
        Check if a given date is a trading day.
        
        Args:
            target_date: The date to check
            
        Returns:
            True if it's a trading day, False otherwise
        """
        trading_hours = self.get_trading_hours(target_date)
        return trading_hours is not None
    
    def filter_trading_hours(self, dataset: StockDataset, target_date: date) -> StockDataset:
        """
        Filter dataset to only include data during official trading hours.
        
        Args:
            dataset: The stock dataset to filter
            target_date: The date to get trading hours for
            
        Returns:
            Filtered dataset containing only trading hours data
            
        Raises:
            ValueError: If the exchange is closed on the target date
        """
        trading_hours = self.get_trading_hours(target_date)
        
        if trading_hours is None:
            raise ValueError(f"Exchange {self.exchange_code} is closed on {target_date}")
        
        open_time, close_time = trading_hours
        
        # Filter the dataset to trading hours
        filtered_dataset = dataset.filter_by_time_range(open_time, close_time)
        
        self.logger.info(
            f"Filtered dataset from {len(dataset)} to {len(filtered_dataset)} "
            f"data points for trading hours {open_time.time()} - {close_time.time()}"
        )
        
        return filtered_dataset
    
    def get_supported_exchanges(self) -> list:
        """
        Get list of supported exchange codes.
        
        Returns:
            List of supported exchange code strings
        """
        try:
            return list(xcals.get_calendar_names())
        except Exception as e:
            self.logger.error(f"Error getting supported exchanges: {e}")
            return []
    
    def get_latest_trading_days(self, latest_date: date, num_days: int) -> list[date]:
        """
        Get the latest N trading days ending with the specified date.
        
        Args:
            latest_date: The most recent date to include
            num_days: Number of trading days to get
            
        Returns:
            List of trading dates in chronological order (oldest first)
        """
        if num_days <= 0:
            return []
        
        trading_days = []
        current_date = latest_date
        
        # Go back in time to find trading days
        days_checked = 0
        max_days_to_check = num_days * 10  # Safety limit to avoid infinite loops
        
        while len(trading_days) < num_days and days_checked < max_days_to_check:
            if self.is_trading_day(current_date):
                trading_days.append(current_date)
            
            # Move to previous day
            current_date = date(current_date.year, current_date.month, current_date.day - 1) \
                if current_date.day > 1 else \
                date(current_date.year, current_date.month - 1, 
                     self._get_last_day_of_month(current_date.year, current_date.month - 1)) \
                if current_date.month > 1 else \
                date(current_date.year - 1, 12, 31)
            
            days_checked += 1
        
        # Return in chronological order (oldest first)
        trading_days.reverse()
        
        self.logger.info(f"Found {len(trading_days)} trading days ending with {latest_date}")
        return trading_days
    
    def _get_last_day_of_month(self, year: int, month: int) -> int:
        """Get the last day of a given month/year."""
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        else:  # February
            return 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28


# Import pandas here to avoid circular imports
import pandas as pd
