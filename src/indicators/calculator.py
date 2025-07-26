"""
Technical indicator calculations using TA-Lib.

This module handles the calculation of technical indicators from OHLCV data.
"""

import logging
import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from datetime import datetime

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False

from ..data.data_models import StockDataset, OHLCVData


class IndicatorCalculator:
    """
    Calculates technical indicators using TA-Lib.
    
    Handles EMA calculations and data alignment with timestamps.
    """
    
    def __init__(self):
        """Initialize the indicator calculator."""
        self.logger = logging.getLogger(__name__)
        
        if not TALIB_AVAILABLE:
            raise ImportError(
                "TA-Lib is not installed. Please install it with: pip install TA-Lib"
            )
    
    def calculate_indicators(self, dataset: StockDataset, 
                           indicators: List[Tuple[str, int, str]]) -> Dict[str, List[Tuple[datetime, Optional[float]]]]:
        """
        Calculate all requested indicators for the dataset.
        
        Args:
            dataset: StockDataset containing OHLCV data
            indicators: List of (indicator_type, period, color) tuples
            
        Returns:
            Dictionary mapping indicator names to list of (timestamp, value) tuples
            
        Raises:
            ValueError: If dataset is empty or calculations fail
        """
        if not dataset or len(dataset) == 0:
            raise ValueError("Dataset is empty, cannot calculate indicators")
        
        self.logger.info(f"Calculating {len(indicators)} indicators for {len(dataset)} data points")
        
        # Extract price data for calculations
        close_prices = np.array([point.close for point in dataset.data])
        timestamps = [point.timestamp for point in dataset.data]
        
        results = {}
        
        for indicator_type, period, color in indicators:
            try:
                indicator_name = f"{indicator_type}_{period}"
                
                if indicator_type == 'ema':
                    values = self._calculate_ema(close_prices, period)
                else:
                    raise ValueError(f"Unsupported indicator type: {indicator_type}")
                
                # Align values with timestamps
                aligned_data = list(zip(timestamps, values))
                results[indicator_name] = aligned_data
                
                # Count valid (non-NaN) values
                valid_count = sum(1 for _, val in aligned_data if val is not None and not np.isnan(val))
                self.logger.info(f"Calculated {indicator_name}: {valid_count}/{len(values)} valid values")
                
            except Exception as e:
                self.logger.error(f"Failed to calculate {indicator_type}_{period}: {e}")
                raise ValueError(f"Failed to calculate {indicator_type}_{period}: {e}")
        
        return results
    
    def _calculate_ema(self, close_prices: np.ndarray, period: int) -> List[Optional[float]]:
        """
        Calculate Exponential Moving Average using TA-Lib.
        
        Args:
            close_prices: Array of closing prices
            period: EMA period
            
        Returns:
            List of EMA values (None for insufficient data periods)
            
        Raises:
            ValueError: If calculation fails
        """
        try:
            # Calculate EMA using TA-Lib
            ema_values = talib.EMA(close_prices, timeperiod=period)
            
            # Convert numpy array to list, handling NaN values
            result = []
            for value in ema_values:
                if np.isnan(value):
                    result.append(None)
                else:
                    result.append(float(value))
            
            self.logger.debug(f"EMA_{period}: {len(result)} values calculated")
            return result
            
        except Exception as e:
            self.logger.error(f"TA-Lib EMA calculation failed: {e}")
            raise ValueError(f"EMA calculation failed: {e}")
    
    def get_indicator_metadata(self, indicators: List[Tuple[str, int, str]]) -> List[Dict[str, Any]]:
        """
        Generate metadata for indicators.
        
        Args:
            indicators: List of (indicator_type, period, color) tuples
            
        Returns:
            List of metadata dictionaries
        """
        metadata = []
        
        for indicator_type, period, color in indicators:
            metadata.append({
                "type": indicator_type,
                "period": period,
                "color": color,
                "name": f"{indicator_type}_{period}"
            })
        
        return metadata
    
    def validate_data_sufficiency(self, dataset: StockDataset, 
                                indicators: List[Tuple[str, int, str]]) -> List[Tuple[str, int, str]]:
        """
        Validate that dataset has sufficient data for indicator calculations.
        
        Args:
            dataset: StockDataset to validate
            indicators: List of indicators to validate
            
        Returns:
            List of valid indicators (may be filtered)
            
        Raises:
            ValueError: If no indicators can be calculated
        """
        if not dataset or len(dataset) == 0:
            raise ValueError("Dataset is empty")
        
        data_length = len(dataset)
        valid_indicators = []
        
        for indicator_type, period, color in indicators:
            # For EMA, we need at least the period length of data
            # TA-Lib typically needs some warm-up period
            min_required = period
            
            if data_length >= min_required:
                valid_indicators.append((indicator_type, period, color))
                self.logger.info(f"Indicator {indicator_type}_{period} is valid (need {min_required}, have {data_length})")
            else:
                self.logger.warning(f"Skipping {indicator_type}_{period}: need {min_required} points, have {data_length}")
        
        if not valid_indicators:
            raise ValueError(f"No indicators can be calculated with {data_length} data points")
        
        return valid_indicators
