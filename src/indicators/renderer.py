"""
Chart renderer for technical indicators.

This module handles adding indicator overlays to lightweight-charts.
"""

import logging
import pandas as pd
from typing import List, Tuple, Dict, Optional
from datetime import datetime

from ..data.data_models import StockDataset


class IndicatorRenderer:
    """
    Renders technical indicators as overlays on stock charts.
    
    Integrates with lightweight-charts-python to add line series.
    """
    
    def __init__(self):
        """Initialize the indicator renderer."""
        self.logger = logging.getLogger(__name__)
    
    def add_indicators_to_chart(self, chart, 
                              indicators_data: Dict[str, List[Tuple[datetime, Optional[float]]]],
                              indicators_config: List[Tuple[str, int, str]]) -> None:
        """
        Add indicator line series to the chart.
        
        Args:
            chart: lightweight-charts Chart instance
            indicators_data: Dictionary mapping indicator names to (timestamp, value) data
            indicators_config: List of (indicator_type, period, color) tuples for configuration
            
        Raises:
            ValueError: If chart or data is invalid
        """
        if not chart:
            raise ValueError("Chart instance is required")
        
        if not indicators_data:
            self.logger.info("No indicators data to render")
            return
        
        self.logger.info(f"Adding {len(indicators_data)} indicators to chart")
        
        # Create color mapping from config
        color_map = {}
        for indicator_type, period, color in indicators_config:
            indicator_name = f"{indicator_type}_{period}"
            color_map[indicator_name] = color
        
        # Add each indicator as a line series
        for indicator_name, data_points in indicators_data.items():
            try:
                color = color_map.get(indicator_name, '#FFFFFF')  # Default to white
                self._add_line_series(chart, indicator_name, data_points, color)
                
            except Exception as e:
                self.logger.error(f"Failed to add indicator {indicator_name}: {e}")
                # Continue with other indicators
    
    def _add_line_series(self, chart, indicator_name: str, 
                        data_points: List[Tuple[datetime, Optional[float]]], 
                        color: str) -> None:
        """
        Add a single indicator line series to the chart.
        
        Args:
            chart: lightweight-charts Chart instance
            indicator_name: Name of the indicator (e.g., "ema_50")
            data_points: List of (timestamp, value) tuples
            color: Hex color code for the line
        """
        # Collect valid data points
        timestamps = []
        values = []
        
        for timestamp, value in data_points:
            if value is not None:
                # Remove timezone info for consistency with price data
                naive_timestamp = timestamp.replace(tzinfo=None) if timestamp.tzinfo else timestamp
                timestamps.append(naive_timestamp)
                values.append(float(value))
        
        if not timestamps:
            self.logger.warning(f"No valid data points for indicator {indicator_name}")
            return
        
        valid_count = len(timestamps)
        self.logger.info(f"Adding {indicator_name} line series: {valid_count} points, color {color}")
        
        try:
            # Create DataFrame with correct column structure for lightweight-charts
            # The library expects a column named after the indicator
            chart_data = {
                'time': timestamps,
                indicator_name: values
            }
            df = pd.DataFrame(chart_data)
            
            # Create line series with specified color
            line = chart.create_line(name=indicator_name, color=color, width=2)
            line.set(df)
            
            self.logger.debug(f"Successfully added {indicator_name} line series")
            
        except Exception as e:
            self.logger.error(f"Failed to create line series for {indicator_name}: {e}")
            raise
    
    def prepare_indicators_for_json(self, indicators_data: Dict[str, List[Tuple[datetime, Optional[float]]]],
                                   dataset: StockDataset) -> List[Dict[str, Optional[float]]]:
        """
        Prepare indicator data for JSON export by aligning with OHLCV timestamps.
        
        Args:
            indicators_data: Dictionary mapping indicator names to (timestamp, value) data
            dataset: Original OHLCV dataset for timestamp alignment
            
        Returns:
            List of dictionaries with indicator values aligned to OHLCV data
        """
        if not indicators_data or not dataset:
            return []
        
        # Create timestamp to indicator values mapping
        indicator_maps = {}
        for indicator_name, data_points in indicators_data.items():
            indicator_maps[indicator_name] = {timestamp: value for timestamp, value in data_points}
        
        # Align with OHLCV timestamps
        aligned_indicators = []
        
        for ohlcv_point in dataset.data:
            timestamp = ohlcv_point.timestamp
            indicator_values = {}
            
            # Get indicator value for this timestamp
            for indicator_name, indicator_map in indicator_maps.items():
                indicator_values[indicator_name] = indicator_map.get(timestamp)
            
            aligned_indicators.append(indicator_values)
        
        self.logger.info(f"Aligned indicators data for {len(aligned_indicators)} timestamps")
        return aligned_indicators
    
    def validate_chart_compatibility(self, chart) -> bool:
        """
        Validate that the chart instance supports indicator overlays.
        
        Args:
            chart: Chart instance to validate
            
        Returns:
            True if chart supports indicators, False otherwise
        """
        try:
            # Check if chart has required methods
            if not hasattr(chart, 'create_line'):
                self.logger.error("Chart does not support line series creation")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Chart compatibility check failed: {e}")
            return False
