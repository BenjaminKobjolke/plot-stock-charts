"""
Data models for OHLCV stock data.

This module defines classes for representing and managing stock market data.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional
import logging


@dataclass
class OHLCVData:
    """
    Represents a single OHLCV (Open, High, Low, Close, Volume) data point.
    
    Attributes:
        timestamp: The datetime of this data point
        open: Opening price
        high: Highest price
        low: Lowest price
        close: Closing price
        volume: Trading volume
    """
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    def to_lightweight_charts_format(self) -> dict:
        """
        Convert to format expected by lightweight-charts-python.
        
        Returns:
            Dictionary with time and OHLCV data
        """
        # Convert timezone-aware timestamp to naive timestamp in local time
        # This ensures the chart displays the local time instead of UTC
        local_time = self.timestamp.replace(tzinfo=None) if self.timestamp.tzinfo else self.timestamp
        
        return {
            'time': local_time,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume
        }


class StockDataset:
    """
    Manages a collection of OHLCV data points.
    
    Provides methods for filtering, sorting, and accessing stock data.
    """
    
    def __init__(self, data: List[OHLCVData]):
        """
        Initialize with a list of OHLCV data points.
        
        Args:
            data: List of OHLCVData objects
        """
        self.data = sorted(data, key=lambda x: x.timestamp)
        self.logger = logging.getLogger(__name__)
    
    def get_latest_date(self) -> Optional[date]:
        """
        Get the latest date in the dataset.
        
        Returns:
            The latest date, or None if dataset is empty
        """
        if not self.data:
            return None
        return self.data[-1].timestamp.date()
    
    def filter_by_date(self, target_date: datetime) -> 'StockDataset':
        """
        Filter data to only include entries from a specific date.
        
        Args:
            target_date: The date to filter by
            
        Returns:
            New StockDataset containing only data from the target date
        """
        filtered_data = [
            point for point in self.data
            if point.timestamp.date() == target_date.date()
        ]
        
        self.logger.info(f"Filtered to {len(filtered_data)} data points for date {target_date.date()}")
        return StockDataset(filtered_data)
    
    def filter_by_time_range(self, start_time: datetime, end_time: datetime) -> 'StockDataset':
        """
        Filter data to only include entries within a time range.
        
        Args:
            start_time: Start of time range (inclusive)
            end_time: End of time range (inclusive)
            
        Returns:
            New StockDataset containing only data within the time range
        """
        # Debug: Log timezone information
        self.logger.info(f"DEBUG: Filtering with time range:")
        self.logger.info(f"DEBUG: Start: {start_time} (timezone: {start_time.tzinfo})")
        self.logger.info(f"DEBUG: End: {end_time} (timezone: {end_time.tzinfo})")
        
        # Debug: Log sample data timestamps
        if self.data:
            self.logger.info(f"DEBUG: Sample data timestamps:")
            for i, point in enumerate(self.data[:3]):  # First 3 points
                self.logger.info(f"DEBUG: Data[{i}]: {point.timestamp} (timezone: {point.timestamp.tzinfo})")
        
        filtered_data = [
            point for point in self.data
            if start_time <= point.timestamp <= end_time
        ]
        
        self.logger.info(f"Filtered to {len(filtered_data)} data points between {start_time} and {end_time}")
        return StockDataset(filtered_data)
    
    def to_lightweight_charts_format(self) -> List[dict]:
        """
        Convert all data to format expected by lightweight-charts-python.
        
        Returns:
            List of dictionaries with time and OHLCV data
        """
        return [point.to_lightweight_charts_format() for point in self.data]
    
    def __len__(self) -> int:
        """Return the number of data points."""
        return len(self.data)
    
    def __bool__(self) -> bool:
        """Return True if dataset contains data."""
        return len(self.data) > 0
    
    def __iter__(self):
        """Allow iteration over data points."""
        return iter(self.data)
