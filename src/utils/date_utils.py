"""
Date and time utility functions.

This module provides utility functions for working with dates, times,
and timezones in the stock chart plotter application.
"""

from datetime import datetime, date, time
from typing import Optional
import logging


def format_date_for_display(target_date: date) -> str:
    """
    Format a date for display purposes.
    
    Args:
        target_date: The date to format
        
    Returns:
        Formatted date string
    """
    return target_date.strftime('%Y-%m-%d')


def format_datetime_for_display(target_datetime: datetime) -> str:
    """
    Format a datetime for display purposes.
    
    Args:
        target_datetime: The datetime to format
        
    Returns:
        Formatted datetime string
    """
    return target_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')


def is_same_date(dt1: datetime, dt2: datetime) -> bool:
    """
    Check if two datetime objects represent the same date.
    
    Args:
        dt1: First datetime
        dt2: Second datetime
        
    Returns:
        True if both datetimes are on the same date
    """
    return dt1.date() == dt2.date()


def get_date_range_string(start_date: date, end_date: Optional[date] = None) -> str:
    """
    Create a string representation of a date range.
    
    Args:
        start_date: Start date
        end_date: End date (optional, defaults to start_date)
        
    Returns:
        Formatted date range string
    """
    if end_date is None or start_date == end_date:
        return format_date_for_display(start_date)
    else:
        return f"{format_date_for_display(start_date)} to {format_date_for_display(end_date)}"


def validate_date_string(date_string: str, date_format: str = '%Y-%m-%d') -> Optional[date]:
    """
    Validate and parse a date string.
    
    Args:
        date_string: Date string to validate
        date_format: Expected date format
        
    Returns:
        Parsed date object, or None if invalid
    """
    try:
        return datetime.strptime(date_string, date_format).date()
    except ValueError:
        return None


def get_timezone_info(dt: datetime) -> str:
    """
    Get timezone information from a datetime object.
    
    Args:
        dt: Datetime object
        
    Returns:
        Timezone information string
    """
    if dt.tzinfo is None:
        return "No timezone info"
    else:
        return str(dt.tzinfo)


class DateTimeHelper:
    """
    Helper class for common date/time operations.
    """
    
    def __init__(self):
        """Initialize the helper."""
        self.logger = logging.getLogger(__name__)
    
    def log_date_info(self, dt: datetime, label: str = "DateTime") -> None:
        """
        Log information about a datetime object.
        
        Args:
            dt: Datetime to log info about
            label: Label for the log message
        """
        self.logger.info(
            f"{label}: {format_datetime_for_display(dt)} "
            f"(Timezone: {get_timezone_info(dt)})"
        )
    
    def get_business_day_info(self, target_date: date) -> dict:
        """
        Get information about whether a date is a business day.
        
        Args:
            target_date: Date to check
            
        Returns:
            Dictionary with business day information
        """
        weekday = target_date.weekday()  # 0 = Monday, 6 = Sunday
        is_weekend = weekday >= 5  # Saturday or Sunday
        
        return {
            'date': target_date,
            'weekday': weekday,
            'weekday_name': target_date.strftime('%A'),
            'is_weekend': is_weekend,
            'is_potential_business_day': not is_weekend
        }
